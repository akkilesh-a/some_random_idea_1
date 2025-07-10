"""FastAPI app with background email polling loop."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint to confirm the server is running."""
    return {"message": "Email Alert System Running"}
