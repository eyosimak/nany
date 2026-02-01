# Recommendation Engine for NANY v0.1
# Rule-based logic for generating action recommendations
#
# Core principles:
# - Friction minimization: reduce barriers to starting
# - Energy matching: match task difficulty to current energy
# - Continuation > initiation: prefer continuing over starting new
# - Constraint dominance: environment overrides ambition
# - Reversibility: prefer actions that can be undone
# - If uncertain, choose the smaller and safer action

from . import models, schemas


def generate_recommendation(
    profile: models.CognitiveProfile,
    environment: models.EnvironmentSnapshot,
    goal: models.Goal
) -> schemas.RecommendationResponse:
    """
    Generate ONE concrete, immediate action based on:
    - User's cognitive profile
    - Current environment
    - Stated goal
    
    Returns a recommendation optimized for execution probability.
    """
    
    # Calculate friction score (higher = more friction to overcome)
    friction_score = _calculate_friction(profile, environment)
    
    # Calculate energy match
    energy_match = _calculate_energy_match(profile, environment)
    
    # Determine action scale based on constraints
    action_scale = _determine_action_scale(
        friction_score, 
        energy_match,
        environment,
        profile
    )
    
    # Generate specific action based on goal and constraints
    action, time_estimate, difficulty, reasoning, fallback = _generate_action(
        goal,
        action_scale,
        profile,
        environment
    )
    
    return schemas.RecommendationResponse(
        recommended_action=action,
        estimated_time_minutes=time_estimate,
        difficulty=difficulty,
        why_this_action=reasoning,
        fallback_action=fallback
    )


def _calculate_friction(
    profile: models.CognitiveProfile,
    environment: models.EnvironmentSnapshot
) -> int:
    """
    Calculate initiation friction score (0-10).
    Higher score = harder to start.
    """
    score = 0
    
    # Profile-based friction
    friction_map = {"low": 0, "medium": 2, "high": 4}
    score += friction_map.get(profile.initiation_friction, 2)
    
    # Time blindness increases friction (hard to gauge task duration)
    blindness_map = {"low": 0, "medium": 1, "high": 2}
    score += blindness_map.get(profile.time_blindness, 1)
    
    # Low energy increases friction
    if environment.energy_level <= 2:
        score += 2
    elif environment.energy_level <= 3:
        score += 1
    
    # External pressure can either help or hurt
    pressure_map = {"none": 1, "low": 0, "medium": 0, "high": 2}
    score += pressure_map.get(environment.external_pressure, 0)
    
    return min(score, 10)


def _calculate_energy_match(
    profile: models.CognitiveProfile,
    environment: models.EnvironmentSnapshot
) -> str:
    """
    Determine appropriate task complexity based on energy.
    Returns: 'minimal', 'low', 'medium'
    """
    energy = environment.energy_level
    
    # Adjust for attention span
    span_penalty = {"short": -1, "medium": 0, "long": 1}
    adjusted_energy = energy + span_penalty.get(profile.attention_span, 0)
    
    if adjusted_energy <= 2:
        return "minimal"
    elif adjusted_energy <= 3:
        return "low"
    else:
        return "medium"


def _determine_action_scale(
    friction_score: int,
    energy_match: str,
    environment: models.EnvironmentSnapshot,
    profile: models.CognitiveProfile
) -> dict:
    """
    Determine the scale of action to recommend.
    
    Returns dict with:
    - max_time: maximum time in minutes
    - complexity: 'trivial', 'simple', 'moderate'
    - approach: 'micro', 'small', 'normal'
    """
    result = {
        "max_time": 30,
        "complexity": "simple",
        "approach": "small"
    }
    
    # Constraint dominance: environment limits everything
    time_available = environment.time_available_minutes
    result["max_time"] = min(time_available, result["max_time"])
    
    # High friction = smaller steps
    if friction_score >= 7:
        result["max_time"] = min(5, result["max_time"])
        result["complexity"] = "trivial"
        result["approach"] = "micro"
    elif friction_score >= 4:
        result["max_time"] = min(15, result["max_time"])
        result["complexity"] = "simple"
        result["approach"] = "small"
    
    # Energy matching
    if energy_match == "minimal":
        result["max_time"] = min(10, result["max_time"])
        result["complexity"] = "trivial"
        result["approach"] = "micro"
    elif energy_match == "low":
        result["max_time"] = min(20, result["max_time"])
        result["complexity"] = "simple"
    
    # Stress response affects approach
    if profile.stress_response == "freeze":
        result["approach"] = "micro"
        result["max_time"] = min(5, result["max_time"])
    elif profile.stress_response == "avoid":
        result["approach"] = "small"
        result["max_time"] = min(15, result["max_time"])
    
    return result


def _generate_action(
    goal: models.Goal,
    action_scale: dict,
    profile: models.CognitiveProfile,
    environment: models.EnvironmentSnapshot
) -> tuple:
    """
    Generate specific action based on goal and constraints.
    
    Returns: (action, time_estimate, difficulty, reasoning, fallback)
    """
    goal_desc = goal.description.lower()
    approach = action_scale["approach"]
    max_time = action_scale["max_time"]
    complexity = action_scale["complexity"]
    
    # Difficulty is based on complexity
    difficulty = "low" if complexity in ["trivial", "simple"] else "medium"
    
    # Build reasoning
    reasoning_parts = []
    
    if approach == "micro":
        reasoning_parts.append("Starting with the smallest possible step to overcome initiation friction.")
    elif approach == "small":
        reasoning_parts.append("Using a small, contained step that matches your current energy.")
    else:
        reasoning_parts.append("Task sized to fit available time and energy.")
    
    if environment.energy_level <= 2:
        reasoning_parts.append("Low energy means keeping demands minimal.")
    
    if profile.initiation_friction == "high":
        reasoning_parts.append("High initiation friction requires extra-easy entry point.")
    
    reasoning = " ".join(reasoning_parts)
    
    # Generate action based on goal type and approach
    action, fallback = _decompose_goal(goal_desc, approach, max_time, environment.context)
    
    # Ensure time estimate fits constraints
    time_estimate = _estimate_time(approach, max_time)
    
    return action, time_estimate, difficulty, reasoning, fallback


def _decompose_goal(goal_desc: str, approach: str, max_time: int, context: str) -> tuple:
    """
    Break down goal into concrete action.
    Returns (action, fallback).
    
    Uses simple pattern matching - not ML.
    """
    
    # Common goal patterns and their micro/small breakdowns
    goal_patterns = {
        "clean": {
            "micro": "Pick up 3 items from the floor and put them away",
            "small": "Clear one surface completely (desk, table, or counter)",
            "normal": "Clean one complete area for {time} minutes",
            "fallback": "Just stand up and observe what needs cleaning for 1 minute"
        },
        "study": {
            "micro": "Open your study materials and read one paragraph",
            "small": "Review notes from the last session for 5 minutes",
            "normal": "Study for {time} minutes with one break",
            "fallback": "Gather your study materials in one place"
        },
        "work": {
            "micro": "Open the project/document you need to work on",
            "small": "Complete one small, defined task from your list",
            "normal": "Work on the highest priority item for {time} minutes",
            "fallback": "Write down exactly what the next step is"
        },
        "exercise": {
            "micro": "Do 5 jumping jacks or stretches right where you are",
            "small": "Take a 5-minute walk around your space",
            "normal": "Do a {time}-minute workout routine",
            "fallback": "Put on your workout clothes"
        },
        "write": {
            "micro": "Write one sentence about your topic",
            "small": "Write for 5 minutes without editing",
            "normal": "Write for {time} minutes, then review",
            "fallback": "Open your document and type a placeholder title"
        },
        "email": {
            "micro": "Open your email and read the subject lines only",
            "small": "Reply to one easy email",
            "normal": "Process emails for {time} minutes",
            "fallback": "Open your email client and close it - just to prove you can"
        },
        "organize": {
            "micro": "Sort 5 items into keep/discard piles",
            "small": "Organize one drawer or small container",
            "normal": "Organize one area for {time} minutes",
            "fallback": "Take a photo of what needs organizing"
        },
        "cook": {
            "micro": "Get out one ingredient you'll need",
            "small": "Prepare ingredients for one part of the meal",
            "normal": "Cook for {time} minutes",
            "fallback": "Decide on exactly what you'll make and nothing else"
        },
        "read": {
            "micro": "Read one page",
            "small": "Read for 5 minutes",
            "normal": "Read for {time} minutes",
            "fallback": "Pick up the book and open to your place"
        },
        "call": {
            "micro": "Write down what you need to say in the call",
            "small": "Make the call with a 2-minute time limit for yourself",
            "normal": "Make the call",
            "fallback": "Find the phone number and add it to your contacts"
        }
    }
    
    # Default patterns for unmatched goals
    default_pattern = {
        "micro": f"Identify and write down the single smallest step toward: {goal_desc}",
        "small": f"Work on '{goal_desc}' for exactly 5 minutes, then stop",
        "normal": f"Work on '{goal_desc}' for {max_time} minutes with a defined stopping point",
        "fallback": f"Set a timer for 2 minutes and just think about '{goal_desc}'"
    }
    
    # Find matching pattern
    matched_pattern = None
    for key, pattern in goal_patterns.items():
        if key in goal_desc:
            matched_pattern = pattern
            break
    
    if not matched_pattern:
        matched_pattern = default_pattern
    
    # Get action for approach level
    action = matched_pattern.get(approach, matched_pattern.get("small"))
    action = action.replace("{time}", str(max_time))
    
    fallback = matched_pattern.get("fallback", f"Just acknowledge this goal exists: {goal_desc}")
    
    return action, fallback


def _estimate_time(approach: str, max_time: int) -> int:
    """Estimate time for action based on approach."""
    time_map = {
        "micro": min(5, max_time),
        "small": min(10, max_time),
        "normal": max_time
    }
    return time_map.get(approach, min(10, max_time))
