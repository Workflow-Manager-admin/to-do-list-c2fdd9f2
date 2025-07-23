from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# PUBLIC_INTERFACE
class UserRegistration(BaseModel):
    """Schema for user registration input."""
    username: str = Field(..., min_length=3, max_length=32, description="Unique username for the user.")
    email: EmailStr = Field(..., description="User's email address.")
    password: str = Field(..., min_length=6, max_length=128, description="Password for the user.")

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Schema for user login input."""
    username: str = Field(..., description="Username of the user.")
    password: str = Field(..., min_length=6, max_length=128, description="Password for the user.")

# PUBLIC_INTERFACE
class UserRead(BaseModel):
    """Schema for returning user details (public)."""
    id: int
    username: str
    email: EmailStr
    created_at: datetime

# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT token returned to the authenticated client."""
    access_token: str
    token_type: str

# PUBLIC_INTERFACE
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=200, description="Title of the task.")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description of the task.")
    due_date: Optional[datetime] = Field(None, description="Optional due date for the task.")

# PUBLIC_INTERFACE
class TaskUpdate(BaseModel):
    """Schema for updating a task (partial fields allowed)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None

# PUBLIC_INTERFACE
class TaskRead(BaseModel):
    """Return schema for a task."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    due_date: Optional[datetime]
    owner_id: int
    created_at: datetime
    updated_at: datetime
