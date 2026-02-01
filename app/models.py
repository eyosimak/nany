# SQLAlchemy models for NANY v0.1
# Each model corresponds to a database table

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class User(Base):
    """
    Simple user model.
    No authentication - just a unique ID to track user data.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cognitive_profile = relationship("CognitiveProfile", back_populates="user", uselist=False)
    environment_snapshots = relationship("EnvironmentSnapshot", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")


class CognitiveProfile(Base):
    """
    Light cognitive profile - non-medical.
    Stores 5 cognitive traits for recommendation engine.
    """
    __tablename__ = "cognitive_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # The 5 cognitive traits
    initiation_friction = Column(String, nullable=False)  # low|medium|high
    attention_span = Column(String, nullable=False)       # short|medium|long
    reward_sensitivity = Column(String, nullable=False)   # low|medium|high
    time_blindness = Column(String, nullable=False)       # low|medium|high
    stress_response = Column(String, nullable=False)      # engage|avoid|freeze
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="cognitive_profile")


class EnvironmentSnapshot(Base):
    """
    Current context snapshot.
    Captures environment at time of goal input.
    """
    __tablename__ = "environment_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    time_available_minutes = Column(Integer, nullable=False)
    energy_level = Column(Integer, nullable=False)        # 1-5
    context = Column(String, nullable=False)              # home|work|school|outside
    external_pressure = Column(String, nullable=False)    # none|low|medium|high
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="environment_snapshots")


class Goal(Base):
    """
    User's stated goal.
    What they want to accomplish.
    """
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    description = Column(String, nullable=False)
    priority = Column(String, nullable=False)             # low|medium|high
    time_horizon = Column(String, nullable=False)         # today|this_week|long_term
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="goals")


class Recommendation(Base):
    """
    Generated recommendation.
    Links to the goal and environment it was based on.
    """
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal_id = Column(Integer, ForeignKey("goals.id"))
    environment_id = Column(Integer, ForeignKey("environment_snapshots.id"))
    
    recommended_action = Column(String, nullable=False)
    estimated_time_minutes = Column(Integer, nullable=False)
    difficulty = Column(String, nullable=False)           # low|medium
    why_this_action = Column(String, nullable=False)
    fallback_action = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="recommendations")


class Feedback(Base):
    """
    User feedback on whether they did the action.
    """
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"))
    
    action_completed = Column(Boolean, nullable=False)
    notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="feedbacks")
