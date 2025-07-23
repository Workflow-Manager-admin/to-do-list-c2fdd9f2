from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints import router as api_router

# OpenAPI tags for better grouping in docs
openapi_tags = [
    {"name": "Authentication", "description": "User registration, login, and access tokens."},
    {"name": "User", "description": "User profile operations."},
    {"name": "Tasks", "description": "CRUD operations on user tasks."},
]

app = FastAPI(
    title="To-Do List API",
    description="Backend API for task management. Features: user auth, JWT, task CRUD. Secure & extensible.",
    version="1.0.0",
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint for service monitoring."""
    return {"message": "Healthy"}

# Register API endpoints
app.include_router(api_router)
