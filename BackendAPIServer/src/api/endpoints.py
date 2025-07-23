from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from . import models
from .db import get_session
from .database_models import User, Task
from .security import get_password_hash, verify_password, create_access_token
from .dependencies import get_current_user

router = APIRouter()

# ===== AUTH ENDPOINTS =====

@router.post("/auth/register", response_model=models.UserRead, summary="Register a new user")
# PUBLIC_INTERFACE
async def register_user(user_in: models.UserRegistration, db: AsyncSession = Depends(get_session)):
    """Register a new user with unique username and email."""
    # Check if username or email taken
    user_q = select(User).where((User.username == user_in.username) | (User.email == user_in.email))
    existing = await db.execute(user_q)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already in use.")
    # Create user
    user_obj = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user_obj)
    await db.commit()
    await db.refresh(user_obj)
    return models.UserRead(
        id=user_obj.id, username=user_obj.username, email=user_obj.email, created_at=user_obj.created_at
    )

@router.post("/auth/login", response_model=models.Token, summary="Login")
# PUBLIC_INTERFACE
async def login_user(user_in: models.UserLogin, db: AsyncSession = Depends(get_session)):
    """Authenticate user and return JWT access token."""
    q = select(User).where(User.username == user_in.username)
    result = await db.execute(q)
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    token = create_access_token(data={"sub": user.username})
    return models.Token(access_token=token, token_type="bearer")

# ===== USER PROFILE =====

@router.get("/users/me", response_model=models.UserRead, summary="Get my profile")
# PUBLIC_INTERFACE
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get details of the current authenticated user."""
    return models.UserRead(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
    )

# ===== TASK CRUD ENDPOINTS =====

@router.post("/tasks/", response_model=models.TaskRead, summary="Create a new task")
# PUBLIC_INTERFACE
async def create_task(task_in: models.TaskCreate, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Create a new task for the authenticated user."""
    task = Task(
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        owner_id=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return models.TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        due_date=task.due_date,
        owner_id=task.owner_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )

@router.get("/tasks/", response_model=List[models.TaskRead], summary="List all my tasks")
# PUBLIC_INTERFACE
async def list_tasks(db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    """List all tasks belonging to the authenticated user."""
    q = select(Task).where(Task.owner_id == current_user.id)
    tasks = (await db.execute(q)).scalars().all()
    return [
        models.TaskRead(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            due_date=task.due_date,
            owner_id=task.owner_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
        for task in tasks
    ]

@router.get("/tasks/{task_id}", response_model=models.TaskRead, summary="Get a specific task")
# PUBLIC_INTERFACE
async def get_task(task_id: int, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Get a single task by ID if owned by the authenticated user."""
    q = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    result = await db.execute(q)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return models.TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        due_date=task.due_date,
        owner_id=task.owner_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )

@router.put("/tasks/{task_id}", response_model=models.TaskRead, summary="Update a task")
# PUBLIC_INTERFACE
async def update_task(
    task_id: int,
    task_in: models.TaskUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update a task's fields if owned by the authenticated user."""
    q = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    result = await db.execute(q)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    for key, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return models.TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        due_date=task.due_date,
        owner_id=task.owner_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )

@router.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
# PUBLIC_INTERFACE
async def delete_task(task_id: int, db: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    """Delete a task owned by the authenticated user."""
    q = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    result = await db.execute(q)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    await db.delete(task)
    await db.commit()
    return None
