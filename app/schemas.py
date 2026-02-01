# Pydantic schemas for API validation
# These match the exact models from requirements

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


# ============================================================
# Cognitive Profile Schema
# ============================================================

class CognitiveProfileCreate(BaseModel):
    """Input schema for creating/updating cognitive profile."""
    initiation_friction: Literal["low", "medium", "high"]
    attention_span: Literal["short", "medium", "long"]
    reward_sensitivity: Literal["low", "medium", "high"]
    time_blindness: Literal["low", "medium", "high"]
    stress_response: Literal["engage", "avoid", "freeze"]


class CognitiveProfileResponse(CognitiveProfileCreate):
    """Response schema including DB fields."""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True


# ============================================================
# Environment Schema
# ============================================================

class EnvironmentCreate(BaseModel):
    """Input schema for environment snapshot."""
    time_available_minutes: int = Field(ge=1, description="Minutes available for task")
    energy_level: int = Field(ge=1, le=5, description="Energy level 1-5")
    context: Literal["home", "work", "school", "outside"]
    external_pressure: Literal["none", "low", "medium", "high"]


class EnvironmentResponse(EnvironmentCreate):
    """Response schema including DB fields."""
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# Goal Schema
# ============================================================

class GoalCreate(BaseModel):
    """Input schema for goal."""
    description: str = Field(min_length=1, max_length=500)
    priority: Literal["low", "medium", "high"]
    time_horizon: Literal["today", "this_week", "long_term"]


class GoalResponse(GoalCreate):
    """Response schema including DB fields."""
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# Recommendation Schema (STRICT OUTPUT FORMAT)
# ============================================================

class RecommendationResponse(BaseModel):
    """
    Recommendation output format - EXACTLY as specified.
    No extra text.
    """
    recommended_action: str
    estimated_time_minutes: int
    difficulty: Literal["low", "medium"]
    why_this_action: str
    fallback_action: str


class RecommendationDBResponse(RecommendationResponse):
    """Response schema including DB fields."""
    id: int
    user_id: int
    goal_id: int
    environment_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# Feedback Schema
# ============================================================

class FeedbackCreate(BaseModel):
    """Input schema for feedback."""
    action_completed: bool
    notes: Optional[str] = None


class FeedbackResponse(FeedbackCreate):
    """Response schema including DB fields."""
    id: int
    user_id: int
    recommendation_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# User Schema
# ============================================================

class UserResponse(BaseModel):
    """User response with ID."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
