import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

BASE = "/api/v1/projects"
SLUG = "test-project-phase1"


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def project(client):
    response = await client.post(BASE, json={"slug": SLUG, "title": "Test Project"})
    assert response.status_code == 201
    yield response.json()
    await client.delete(f"{BASE}/{SLUG}")


async def test_list_projects(client):
    response = await client.get(BASE)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


async def test_create_project(project):
    assert project["slug"] == SLUG
    assert project["title"] == "Test Project"
    assert "id" in project


async def test_get_project_by_slug(client, project):
    response = await client.get(f"{BASE}/{SLUG}")
    assert response.status_code == 200
    assert response.json()["slug"] == SLUG


async def test_get_project_not_found(client):
    response = await client.get(f"{BASE}/nonexistent-slug")
    assert response.status_code == 404


async def test_update_project(client, project):
    response = await client.patch(f"{BASE}/{SLUG}", json={"title": "Updated Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


async def test_delete_project(client):
    slug = "project-to-delete"
    await client.post(BASE, json={"slug": slug, "title": "To Delete"})
    response = await client.delete(f"{BASE}/{slug}")
    assert response.status_code == 204
    assert (await client.get(f"{BASE}/{slug}")).status_code == 404
