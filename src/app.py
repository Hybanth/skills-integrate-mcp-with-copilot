"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import json

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

ACTIVITIES_FILE = os.path.join(current_dir, "activities.json")

def load_activities():
    with open(ACTIVITIES_FILE, "r") as f:
        return json.load(f)

def save_activities(activities):
    with open(ACTIVITIES_FILE, "w") as f:
        json.dump(activities, f, indent=2)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(category: str = None, search: str = None, sort: str = None):
    """Get all activities, with optional filter, search, and sort"""
    activities = load_activities()
    filtered = activities
    # Filter by category
    if category:
        filtered = [a for a in filtered if a.get("category", "").lower() == category.lower()]
    # Search by name or description
    if search:
        search_lower = search.lower()
        filtered = [a for a in filtered if search_lower in a["name"].lower() or search_lower in a["description"].lower()]
    # Sort
    if sort == "name":
        filtered = sorted(filtered, key=lambda a: a["name"].lower())
    elif sort == "category":
        filtered = sorted(filtered, key=lambda a: a.get("category", "").lower())
    elif sort == "participants":
        filtered = sorted(filtered, key=lambda a: len(a.get("participants", [])), reverse=True)
    return filtered


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activities = load_activities()
    for activity in activities:
        if activity["name"].lower() == activity_name.lower():
            if email in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student is already signed up")
            if len(activity["participants"]) >= activity["max_participants"]:
                raise HTTPException(status_code=400, detail="Activity is full")
            activity["participants"].append(email)
            save_activities(activities)
            return {"message": f"Signed up {email} for {activity['name']}"}
    raise HTTPException(status_code=404, detail="Activity not found")


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    activities = load_activities()
    for activity in activities:
        if activity["name"].lower() == activity_name.lower():
            if email not in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
            activity["participants"].remove(email)
            save_activities(activities)
            return {"message": f"Unregistered {email} from {activity['name']}"}
    raise HTTPException(status_code=404, detail="Activity not found")
