"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from pathlib import Path

from database import init_db, get_db, populate_initial_data
from models import Activity, Participant

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    await populate_initial_data()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
async def get_activities(db: AsyncSession = Depends(get_db)):
    """Get all activities with their participants"""
    result = await db.execute(select(Activity))
    activities = result.scalars().all()
    
    # Convert to the expected format
    activities_dict = {}
    for activity in activities:
        activities_dict[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [p.email for p in activity.participants]
        }
    
    return activities_dict


@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(activity_name: str, email: str, db: AsyncSession = Depends(get_db)):
    """Sign up a student for an activity"""
    # Find the activity
    result = await db.execute(select(Activity).where(Activity.name == activity_name))
    activity = result.scalars().first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if activity is full
    if len(activity.participants) >= activity.max_participants:
        raise HTTPException(status_code=400, detail="Activity is full")
    
    # Find or create participant
    result = await db.execute(select(Participant).where(Participant.email == email))
    participant = result.scalars().first()
    
    if not participant:
        participant = Participant(email=email)
        db.add(participant)
        await db.flush()
    
    # Check if student is already signed up
    if participant in activity.participants:
        raise HTTPException(status_code=400, detail="Student is already signed up")
    
    # Add student to activity
    activity.participants.append(participant)
    await db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
async def unregister_from_activity(activity_name: str, email: str, db: AsyncSession = Depends(get_db)):
    """Unregister a student from an activity"""
    # Find the activity
    result = await db.execute(select(Activity).where(Activity.name == activity_name))
    activity = result.scalars().first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Find the participant
    result = await db.execute(select(Participant).where(Participant.email == email))
    participant = result.scalars().first()
    
    if not participant or participant not in activity.participants:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
    
    # Remove student from activity
    activity.participants.remove(participant)
    await db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}
