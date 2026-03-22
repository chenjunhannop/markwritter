"""FastAPI application entry point for Markwritter API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import chat, logs, skills

app = FastAPI(
    title="Markwritter API",
    description="Agent orchestration framework API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills.router)
app.include_router(chat.router)
app.include_router(logs.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
