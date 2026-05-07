from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.core.database import get_pool
from app.models.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services import project_service

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    pool = await get_pool()
    items, total = await project_service.get_all(pool, page, size)
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{slug}", response_model=ProjectResponse)
async def get_project(slug: str):
    pool = await get_pool()
    project = await project_service.get_by_slug(pool, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(data: ProjectCreate):
    pool = await get_pool()
    return await project_service.create(pool, data)


@router.patch("/{slug}", response_model=ProjectResponse)
async def update_project(slug: str, data: ProjectUpdate):
    pool = await get_pool()
    project = await project_service.update(pool, slug, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{slug}", status_code=204)
async def delete_project(slug: str):
    pool = await get_pool()
    deleted = await project_service.delete(pool, slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
