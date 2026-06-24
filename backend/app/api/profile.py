from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.services.file_parser import extract_text_from_file
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services.cv_parser import parse_cv
from app.core.dependencies import get_current_user


router = APIRouter()


@router.post("/parse-cv", response_model=ProfileResponse)
async def parse_cv_endpoint(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cv_text = payload.get("text")
    if not cv_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El campo text es requerido")

    extracted = await parse_cv(cv_text)

    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    existing = result.scalar_one_or_none()

    if existing:
        existing.raw_text = cv_text
        existing.full_name = extracted.get("full_name")
        existing.professional_title = extracted.get("professional_title")
        existing.email = extracted.get("email")
        existing.skills = extracted.get("skills", [])
        existing.experience = extracted.get("experience", [])
        existing.projects = extracted.get("projects", [])
        existing.education = extracted.get("education", [])
        existing.languages = extracted.get("languages", [])
        existing.links = extracted.get("links", {})
        await db.flush()
        return existing

    profile = UserProfile(
        user_id=user.id,
        raw_text=cv_text,
        full_name=extracted.get("full_name"),
        professional_title=extracted.get("professional_title"),
        email=extracted.get("email"),
        skills=extracted.get("skills", []),
        experience=extracted.get("experience", []),
        projects=extracted.get("projects", []),
        education=extracted.get("education", []),
        languages=extracted.get("languages", []),
        links=extracted.get("links", {}),
    )
    db.add(profile)
    await db.flush()
    return profile


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")

    return profile


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Perfil no encontrado")

    if payload.full_name is not None:
        profile.full_name = payload.full_name
    if payload.professional_title is not None:
        profile.professional_title = payload.professional_title
    if payload.email is not None:
        profile.email = payload.email
    if payload.skills is not None:
        profile.skills = payload.skills
    if payload.experience is not None:
        profile.experience = [e.model_dump() for e in payload.experience]
    if payload.projects is not None:
        profile.projects = [p.model_dump() for p in payload.projects]
    if payload.education is not None:
        profile.education = [e.model_dump() for e in payload.education]
    if payload.languages is not None:
        profile.languages = payload.languages
    if payload.links is not None:
        profile.links = payload.links.model_dump()

    await db.flush()
    return profile

@router.post("/upload-cv", response_model=ProfileResponse)
async def upload_cv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se recibió ningún archivo")

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo está vacío")

    try:
        cv_text = extract_text_from_file(file.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not cv_text.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo extraer texto del archivo")

    extracted = await parse_cv(cv_text)

    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    existing = result.scalar_one_or_none()

    if existing:
        existing.raw_text = cv_text
        existing.full_name = extracted.get("full_name")
        existing.professional_title = extracted.get("professional_title")
        existing.email = extracted.get("email")
        existing.skills = extracted.get("skills", [])
        existing.experience = extracted.get("experience", [])
        existing.projects = extracted.get("projects", [])
        existing.education = extracted.get("education", [])
        existing.languages = extracted.get("languages", [])
        existing.links = extracted.get("links", {})
        await db.flush()
        return existing

    profile = UserProfile(
        user_id=user.id,
        raw_text=cv_text,
        full_name=extracted.get("full_name"),
        professional_title=extracted.get("professional_title"),
        email=extracted.get("email"),
        skills=extracted.get("skills", []),
        experience=extracted.get("experience", []),
        projects=extracted.get("projects", []),
        education=extracted.get("education", []),
        languages=extracted.get("languages", []),
        links=extracted.get("links", {}),
    )
    db.add(profile)
    await db.flush()
    return profile