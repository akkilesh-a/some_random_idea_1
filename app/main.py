"""FastAPI app with background email polling loop using lifespan."""

from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from app.email_listener import check_for_new_emails


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


@app.get("/")
async def root():
    """Root endpoint to confirm the server is running."""
    return {"message": "Email Alert System Running"}
