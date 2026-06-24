from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.session import get_db
from app.models.tracker import JobApplication
from app.models.user import User
from app.schemas.tracker import JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse
from app.core.dependencies import get_current_user
import uuid

router = APIRouter()


@router.get("/", response_model=list[JobApplicationResponse])
async def list_applications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JobApplication)
        .where(JobApplication.user_id == user.id)
        .order_by(JobApplication.created_at.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=JobApplicationResponse)
async def create_application(
    payload: JobApplicationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    app = JobApplication(id=uuid.uuid4(), user_id=user.id, **payload.model_dump())
    db.add(app)
    await db.flush()
    return app


@router.put("/{app_id}", response_model=JobApplicationResponse)
async def update_application(
    app_id: uuid.UUID,
    payload: JobApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == app_id,
            JobApplication.user_id == user.id,
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aplicación no encontrada")

    for key, value in payload.model_dump(exclude_none=True).items():
        setattr(app, key, value)

    await db.flush()
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(JobApplication).where(
            JobApplication.id == app_id,
            JobApplication.user_id == user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aplicación no encontrada")

    await db.execute(delete(JobApplication).where(JobApplication.id == app_id))