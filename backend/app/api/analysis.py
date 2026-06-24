from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.session import get_db
from app.models.analysis import Analysis
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisListItem
from app.services.llm import analyze_job_offer
from app.core.dependencies import get_current_user
import uuid

router = APIRouter()


@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    payload: AnalysisCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debes crear tu perfil antes de analizar una oferta")

    profile_dict = {"skills": profile.skills, "experience": profile.experience}

    try:
        llm_result = await analyze_job_offer(profile_dict, payload.job_text)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    analysis = Analysis(
        user_id=user.id,
        job_title=llm_result.get("job_title"),
        company=llm_result.get("company"),
        job_text=payload.job_text,
        required_skills=llm_result["required_skills"],
        matching_skills=llm_result["matching_skills"],
        missing_skills=llm_result["missing_skills"],
        match_score=llm_result["match_score"],
        summary=llm_result["summary"],
    )
    db.add(analysis)
    await db.flush()
    return analysis


@router.get("/", response_model=list[AnalysisListItem])
async def get_analyses(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == user.id)
        .order_by(Analysis.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Análisis no encontrado")

    return analysis


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Análisis no encontrado")

    await db.execute(delete(Analysis).where(Analysis.id == analysis_id))