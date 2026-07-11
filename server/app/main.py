from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered health literacy platform that translates medical reports into simple, personalized explanations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {"project": settings.PROJECT_NAME, "status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "healthy"}
