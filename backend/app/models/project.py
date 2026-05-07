from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    slug: str
    title: str
    problem_statement: str | None = None
    methodology: str | None = None
    results_impact: str | None = None
    metrics: dict | None = None
    tech_stack: list[str] = []
    categories: list[str] = []
    github_url: str | None = None
    demo_url: str | None = None
    notebook_url: str | None = None
    thumbnail_url: str | None = None
    has_ml_demo: bool = False
    ml_endpoint: str | None = None
    featured: bool = False
    display_order: int = 0


class ProjectUpdate(BaseModel):
    slug: str | None = None
    title: str | None = None
    problem_statement: str | None = None
    methodology: str | None = None
    results_impact: str | None = None
    metrics: dict | None = None
    tech_stack: list[str] | None = None
    categories: list[str] | None = None
    github_url: str | None = None
    demo_url: str | None = None
    notebook_url: str | None = None
    thumbnail_url: str | None = None
    has_ml_demo: bool | None = None
    ml_endpoint: str | None = None
    featured: bool | None = None
    display_order: int | None = None


class ProjectResponse(BaseModel):
    id: UUID
    slug: str
    title: str
    problem_statement: str | None
    methodology: str | None
    results_impact: str | None
    metrics: dict | None
    tech_stack: list[str]
    categories: list[str]
    github_url: str | None
    demo_url: str | None
    notebook_url: str | None
    thumbnail_url: str | None
    has_ml_demo: bool
    ml_endpoint: str | None
    featured: bool
    display_order: int
    created_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectResponse]
    total: int
    page: int
    size: int
