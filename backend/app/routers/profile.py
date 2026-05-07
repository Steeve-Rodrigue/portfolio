from fastapi import APIRouter, HTTPException

from app.core.database import get_pool
from app.models.profile import ProfileResponse, ProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/api/v1/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile():
    pool = await get_pool()
    profile = await profile_service.get(pool)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("", response_model=ProfileResponse)
async def update_profile(data: ProfileUpdate):
    pool = await get_pool()
    profile = await profile_service.update(pool, data)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
