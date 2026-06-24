from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AdminUserResponse, AdminCreateUser, AdminToggleUser
from app.core.dependencies import get_admin_user
from app.core.security import hash_password
import uuid

router = APIRouter()


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.post("/users", response_model=AdminUserResponse)
async def create_user(
    payload: AdminCreateUser,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")

    user = User(
        id=uuid.uuid4(),
        email=payload.email,
        password=hash_password(payload.password),
        is_admin=payload.is_admin,
    )
    db.add(user)
    await db.flush()
    return user


@router.put("/users/{user_id}/toggle", response_model=AdminUserResponse)
async def toggle_user(
    user_id: uuid.UUID,
    payload: AdminToggleUser,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    if str(user_id) == str(admin.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes pausar tu propia cuenta")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    user.is_active = payload.is_active
    await db.flush()
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    if str(user_id) == str(admin.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes borrar tu propia cuenta")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    await db.execute(delete(User).where(User.id == user_id))