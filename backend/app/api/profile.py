from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services.cv_parser import parse_cv
import uuid

router = APIRouter()

# ID fijo mientras no tenemos auth, Fase 2 lo reemplaza
TEMP_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@router.post("/parse-cv", response_model=ProfileResponse)
async def parse_cv_endpoint(payload: dict, db: AsyncSession = Depends(get_db)):
    cv_text = payload.get("text")
    if not cv_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo text es requerido"
        )

    extracted = await parse_cv(cv_text)

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == TEMP_USER_ID)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.raw_text = cv_text
        existing.skills = extracted["skills"]
        existing.experience = extracted["experience"]
        await db.flush()
        return existing

    profile = UserProfile(
        user_id=TEMP_USER_ID,
        raw_text=cv_text,
        skills=extracted["skills"],
        experience=extracted["experience"],
    )
    db.add(profile)
    await db.flush()
    return profile


@router.get("/", response_model=ProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == TEMP_USER_ID)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado"
        )

    return profile


@router.put("/", response_model=ProfileResponse)
async def update_profile(payload: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == TEMP_USER_ID)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado"
        )

    if payload.skills is not None:
        profile.skills = payload.skills
    if payload.experience is not None:
        profile.experience = [e.model_dump() for e in payload.experience]

    await db.flush()
    return profile