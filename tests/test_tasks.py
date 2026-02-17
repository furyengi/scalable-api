import pytest


@pytest.mark.asyncio
async def test_create_task(client, auth_headers):
    response = await client.post("/api/v1/tasks/", json={"title": "Write unit tests", "priority": "high"}, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Write unit tests"
    assert response.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_list_tasks(client, auth_headers):
    response = await client.get("/api/v1/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert "tasks" in response.json()


@pytest.mark.asyncio
async def test_update_task(client, auth_headers):
    create = await client.post("/api/v1/tasks/", json={"title": "To update"}, headers=auth_headers)
    task_id = create.json()["id"]
    update = await client.patch(f"/api/v1/tasks/{task_id}", json={"status": "in_progress"}, headers=auth_headers)
    assert update.status_code == 200
    assert update.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_task(client, auth_headers):
    create = await client.post("/api/v1/tasks/", json={"title": "To delete"}, headers=auth_headers)
    task_id = create.json()["id"]
    assert (await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)).status_code == 204
    assert (await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)).status_code == 404
