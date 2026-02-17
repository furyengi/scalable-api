from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.redis_client import redis_client
from app.core.config import settings
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

router = APIRouter()


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    archived: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"tasks:user:{current_user.id}:p{page}:pp{per_page}:s{status}:pr{priority}:a{archived}"
    cached = await redis_client.get(cache_key)
    if cached:
        return cached

    conditions = [Task.owner_id == current_user.id, Task.is_archived == archived]
    if status:
        conditions.append(Task.status == status)
    if priority:
        conditions.append(Task.priority == priority)

    total = (await db.execute(select(func.count(Task.id)).where(and_(*conditions)))).scalar()
    tasks = (await db.execute(select(Task).where(and_(*conditions)).order_by(Task.created_at.desc()).offset((page - 1) * per_page).limit(per_page))).scalars().all()

    response = {"tasks": [TaskResponse.model_validate(t).model_dump() for t in tasks], "total": total, "page": page, "per_page": per_page, "pages": -(-total // per_page)}
    await redis_client.set(cache_key, response, ttl=settings.CACHE_TTL_MEDIUM)
    return response


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(task_in: TaskCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = Task(**task_in.model_dump(), owner_id=current_user.id, status="pending")
    db.add(task)
    await db.flush()
    await db.refresh(task)
    await redis_client.delete_pattern(f"tasks:user:{current_user.id}:*")
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cached = await redis_client.get(f"task:{task_id}")
    if cached:
        return cached
    result = await db.execute(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await redis_client.set(f"task:{task_id}", TaskResponse.model_validate(task).model_dump(), ttl=settings.CACHE_TTL_SHORT)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.flush()
    await db.refresh(task)
    await redis_client.delete(f"task:{task_id}")
    await redis_client.delete_pattern(f"tasks:user:{current_user.id}:*")
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.owner_id == current_user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await redis_client.delete(f"task:{task_id}")
    await redis_client.delete_pattern(f"tasks:user:{current_user.id}:*")
