from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import profile, analysis, auth, admin, tracker
from app.models.user import User
from app.models.profile import UserProfile
from app.models.analysis import Analysis
from app.models.tracker import JobApplication

app = FastAPI(title="Job Offer Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(tracker.router, prefix="/tracker", tags=["tracker"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])


@app.get("/health")
async def health():
    return {"status": "ok"}