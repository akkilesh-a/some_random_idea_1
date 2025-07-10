"""FastAPI app with background email polling loop using lifespan."""

from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.email_listener import check_for_new_emails
from app.llm_filter import update_student_profile, get_student_profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifespan context."""
    task = asyncio.create_task(poll_email_loop())
    yield
    task.cancel()


async def poll_email_loop():
    """Infinite loop to periodically check for new emails."""
    while True:
        print("🔁 Checking for new placement emails...")
        await asyncio.to_thread(check_for_new_emails)
        await asyncio.sleep(60)


app = FastAPI(lifespan=lifespan)


class ProfileUpdate(BaseModel):
    specialization: str = ""


@app.get("/")
async def root():
    """Root endpoint to confirm the server is running."""
    return {"message": "Email Alert System Running"}


@app.get("/profile")
async def get_profile():
    """Get current student profile."""
    return {"profile": get_student_profile()}


@app.post("/profile")
async def update_profile(profile_data: ProfileUpdate):
    """Update student profile for personalized email filtering."""
    try:
        # Filter out empty values
        updates = {k: v for k, v in profile_data.dict().items() if v}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        updated_profile = update_student_profile(**updates)
        return {
            "message": "Profile updated successfully",
            "profile": updated_profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")
