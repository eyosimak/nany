# NANY v0.1 - FastAPI Main Application
# Decision-support tool for neurodivergent users

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from .database import engine, get_db, Base
from . import models, schemas, crud, rules

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="NANY v0.1",
    description="Decision-support tool for neurodivergent users",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# ============================================================
# Routes
# ============================================================

@app.get("/")
async def root():
    """Serve frontend."""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "NANY v0.1 API", "docs": "/docs"}


@app.post("/users", response_model=schemas.UserResponse)
def create_user(db: Session = Depends(get_db)):
    """Create a new user. Returns user ID."""
    return crud.create_user(db)


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/{user_id}/profile", response_model=schemas.CognitiveProfileResponse)
def save_cognitive_profile(
    user_id: int,
    profile: schemas.CognitiveProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Save cognitive profile for user.
    Creates new or updates existing profile.
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.create_or_update_cognitive_profile(db, user_id, profile)


@app.get("/users/{user_id}/profile", response_model=schemas.CognitiveProfileResponse)
def get_cognitive_profile(user_id: int, db: Session = Depends(get_db)):
    """Get cognitive profile for user."""
    profile = crud.get_cognitive_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.post("/users/{user_id}/environment", response_model=schemas.EnvironmentResponse)
def save_environment(
    user_id: int,
    env: schemas.EnvironmentCreate,
    db: Session = Depends(get_db)
):
    """Save current environment snapshot."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.create_environment(db, user_id, env)


@app.post("/users/{user_id}/goal", response_model=schemas.GoalResponse)
def save_goal(
    user_id: int,
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db)
):
    """Save user's goal."""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.create_goal(db, user_id, goal)


@app.get("/users/{user_id}/recommend", response_model=schemas.RecommendationResponse)
def get_recommendation(user_id: int, db: Session = Depends(get_db)):
    """
    Generate recommendation based on:
    - User's cognitive profile
    - Latest environment snapshot
    - Latest goal
    
    Returns ONE concrete, immediate action.
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = crud.get_cognitive_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=400, detail="Cognitive profile required")
    
    environment = crud.get_latest_environment(db, user_id)
    if not environment:
        raise HTTPException(status_code=400, detail="Environment snapshot required")
    
    goal = crud.get_latest_goal(db, user_id)
    if not goal:
        raise HTTPException(status_code=400, detail="Goal required")
    
    # Generate recommendation using rules engine
    recommendation = rules.generate_recommendation(profile, environment, goal)
    
    # Store recommendation
    crud.create_recommendation(
        db, user_id, goal.id, environment.id, recommendation
    )
    
    return recommendation


@app.post("/users/{user_id}/feedback", response_model=schemas.FeedbackResponse)
def save_feedback(
    user_id: int,
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Record whether user completed the action.
    Links to most recent recommendation.
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    recommendation = crud.get_latest_recommendation(db, user_id)
    if not recommendation:
        raise HTTPException(status_code=400, detail="No recommendation to give feedback on")
    
    return crud.create_feedback(db, user_id, recommendation.id, feedback)


# Health check
@app.get("/health")
def health_check():
    """API health check."""
    return {"status": "healthy", "version": "0.1.0"}
