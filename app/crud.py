# CRUD operations for NANY v0.1
# Create and read operations for all models

from sqlalchemy.orm import Session
from typing import Optional

from . import models, schemas


# ============================================================
# User CRUD
# ============================================================

def create_user(db: Session) -> models.User:
    """Create a new user with auto-generated ID."""
    user = models.User()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


# ============================================================
# Cognitive Profile CRUD
# ============================================================

def create_or_update_cognitive_profile(
    db: Session,
    user_id: int,
    profile: schemas.CognitiveProfileCreate
) -> models.CognitiveProfile:
    """Create or update cognitive profile for user."""
    existing = db.query(models.CognitiveProfile).filter(
        models.CognitiveProfile.user_id == user_id
    ).first()
    
    if existing:
        # Update existing profile
        for key, value in profile.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new profile
        db_profile = models.CognitiveProfile(
            user_id=user_id,
            **profile.model_dump()
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile


def get_cognitive_profile(db: Session, user_id: int) -> Optional[models.CognitiveProfile]:
    """Get cognitive profile for user."""
    return db.query(models.CognitiveProfile).filter(
        models.CognitiveProfile.user_id == user_id
    ).first()


# ============================================================
# Environment CRUD
# ============================================================

def create_environment(
    db: Session,
    user_id: int,
    env: schemas.EnvironmentCreate
) -> models.EnvironmentSnapshot:
    """Create environment snapshot for user."""
    db_env = models.EnvironmentSnapshot(
        user_id=user_id,
        **env.model_dump()
    )
    db.add(db_env)
    db.commit()
    db.refresh(db_env)
    return db_env


def get_latest_environment(db: Session, user_id: int) -> Optional[models.EnvironmentSnapshot]:
    """Get most recent environment snapshot for user."""
    return db.query(models.EnvironmentSnapshot).filter(
        models.EnvironmentSnapshot.user_id == user_id
    ).order_by(models.EnvironmentSnapshot.created_at.desc()).first()


# ============================================================
# Goal CRUD
# ============================================================

def create_goal(
    db: Session,
    user_id: int,
    goal: schemas.GoalCreate
) -> models.Goal:
    """Create goal for user."""
    db_goal = models.Goal(
        user_id=user_id,
        **goal.model_dump()
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_latest_goal(db: Session, user_id: int) -> Optional[models.Goal]:
    """Get most recent goal for user."""
    return db.query(models.Goal).filter(
        models.Goal.user_id == user_id
    ).order_by(models.Goal.created_at.desc()).first()


# ============================================================
# Recommendation CRUD
# ============================================================

def create_recommendation(
    db: Session,
    user_id: int,
    goal_id: int,
    environment_id: int,
    recommendation: schemas.RecommendationResponse
) -> models.Recommendation:
    """Store generated recommendation."""
    db_rec = models.Recommendation(
        user_id=user_id,
        goal_id=goal_id,
        environment_id=environment_id,
        **recommendation.model_dump()
    )
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec


def get_latest_recommendation(db: Session, user_id: int) -> Optional[models.Recommendation]:
    """Get most recent recommendation for user."""
    return db.query(models.Recommendation).filter(
        models.Recommendation.user_id == user_id
    ).order_by(models.Recommendation.created_at.desc()).first()


# ============================================================
# Feedback CRUD
# ============================================================

def create_feedback(
    db: Session,
    user_id: int,
    recommendation_id: int,
    feedback: schemas.FeedbackCreate
) -> models.Feedback:
    """Store user feedback on recommendation."""
    db_feedback = models.Feedback(
        user_id=user_id,
        recommendation_id=recommendation_id,
        **feedback.model_dump()
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback
