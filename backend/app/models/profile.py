from datetime import datetime

from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    tagline: str | None = None
    availability_status: str | None = None
    is_open_to_work: bool | None = None
    location: str | None = None
    email: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    calendly_url: str | None = None
    social_links: dict | None = None
    ethics_statement: str | None = None
    communication_style: str | None = None
    work_preference: str | None = None
    fun_fact: str | None = None


class ProfileResponse(BaseModel):
    name: str
    title: str
    tagline: str | None
    availability_status: str | None
    is_open_to_work: bool
    location: str | None
    email: str | None
    github_url: str | None
    linkedin_url: str | None
    calendly_url: str | None
    social_links: dict | None
    ethics_statement: str | None
    communication_style: str | None
    work_preference: str | None
    fun_fact: str | None
    updated_at: datetime
