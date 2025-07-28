"""
FastAPI main application module.

This module configures the FastAPI application, middleware, error handlers,
and all API routes for the Checklist application.
"""

import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from sqlalchemy.orm import Session
from uuid import UUID

from .database import get_db
from . import models, schemas, crud, auth
from .crud import CRUDError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app configuration
app = FastAPI(
    title="Checklist API",
    version="1.0.0",
    description="API for managing checklists and tasks with Google OAuth authentication",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
allowed_origins = [
    "http://localhost:3000",  # Next.js development (default)
    "http://localhost:3001",  # Next.js development (alternative port)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    os.getenv("FRONTEND_URL", "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)


# Global Exception Handlers
@app.exception_handler(CRUDError)
async def crud_exception_handler(request: Request, exc: CRUDError):
    """Handle CRUD operation errors."""
    logger.error(f"CRUD error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database operation failed", "error_code": "crud_error"}
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    logger.warning(f"Validation error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "error_code": "validation_error"}
    )


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Handle internal server errors."""
    logger.error(f"Internal server error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error_code": "internal_error"}
    )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} for {request.method} {request.url} "
        f"in {process_time:.4f}s"
    )
    
    return response


# Root and Health Check Endpoints
@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Checklist API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "checklist-api"}


# Authentication Endpoints
@app.post(
    "/auth/google", 
    response_model=schemas.TokenResponse,
    tags=["Authentication"],
    summary="Google OAuth Login",
    description="Authenticate user with Google OAuth and receive JWT token"
)
async def google_login(
    google_data: schemas.GoogleOAuthData,
    db: Session = Depends(get_db)
):
    """Login with Google OAuth and get JWT token."""
    try:
        token_response = await auth.authenticate_google_user(google_data, db)
        logger.info(f"User authenticated successfully: {token_response.user.email}")
        return token_response
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise


@app.get(
    "/auth/me",
    response_model=schemas.UserResponse,
    tags=["Authentication"],
    summary="Get Current User",
    description="Get current authenticated user information"
)
async def get_current_user_info(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get current authenticated user information."""
    return schemas.UserResponse.from_orm(current_user)


# Checklist Endpoints
@app.get(
    "/checklists",
    response_model=schemas.PaginatedResponse,
    tags=["Checklists"],
    summary="List User Checklists",
    description="Get paginated list of user's checklists"
)
async def list_checklists(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's checklists with pagination."""
    try:
        # Validate pagination parameters
        if skip < 0 or limit <= 0 or limit > 100:
            raise ValueError("Invalid pagination parameters")
        
        checklists, total = crud.get_checklists(db, current_user.id, skip, limit)
        
        # Convert to summary format (without full items)
        checklist_summaries = []
        for checklist in checklists:
            summary = schemas.ChecklistSummary(
                id=checklist.id,
                title=checklist.title,
                description=checklist.description,
                created_at=checklist.created_at,
                updated_at=checklist.updated_at,
                total_items=checklist.total_items,
                completed_items=checklist.completed_items,
                completion_percentage=checklist.completion_percentage
            )
            checklist_summaries.append(summary)
        
        return schemas.PaginatedResponse(
            items=checklist_summaries,
            total=total,
            skip=skip,
            limit=limit
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/checklists",
    response_model=schemas.ChecklistResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Checklists"],
    summary="Create Checklist",
    description="Create a new checklist with optional initial items"
)
async def create_checklist(
    checklist: schemas.ChecklistCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new checklist."""
    try:
        db_checklist = crud.create_checklist(db, checklist, current_user.id)
        return schemas.ChecklistResponse.from_orm(db_checklist)
    except CRUDError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/checklists/{checklist_id}",
    response_model=schemas.ChecklistResponse,
    tags=["Checklists"],
    summary="Get Checklist",
    description="Get a specific checklist with all its items"
)
async def get_checklist(
    checklist_id: UUID,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific checklist."""
    try:
        db_checklist = crud.get_checklist(db, checklist_id, current_user.id)
        if not db_checklist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist not found"
            )
        return schemas.ChecklistResponse.from_orm(db_checklist)
    except CRUDError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put(
    "/checklists/{checklist_id}",
    response_model=schemas.ChecklistResponse,
    tags=["Checklists"],
    summary="Update Checklist",
    description="Update checklist title and description"
)
async def update_checklist(
    checklist_id: UUID,
    checklist_update: schemas.ChecklistUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a checklist."""
    try:
        db_checklist = crud.update_checklist(db, checklist_id, checklist_update, current_user.id)
        if not db_checklist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist not found"
            )
        return schemas.ChecklistResponse.from_orm(db_checklist)
    except CRUDError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/checklists/{checklist_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Checklists"],
    summary="Delete Checklist",
    description="Delete a checklist and all its items"
)
async def delete_checklist(
    checklist_id: UUID,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a checklist."""
    try:
        deleted = crud.delete_checklist(db, checklist_id, current_user.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist not found"
            )
        return None
    except CRUDError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Checklist Item Endpoints
@app.post(
    "/checklists/{checklist_id}/items",
    response_model=schemas.ChecklistItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Checklist Items"],
    summary="Add Item to Checklist",
    description="Add a new item to an existing checklist"
)
async def create_checklist_item(
    checklist_id: UUID,
    item: schemas.ChecklistItemCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a new item to a checklist."""
    try:
        db_item = crud.create_checklist_item(db, item, checklist_id, current_user.id)
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist not found"
            )
        return schemas.ChecklistItemResponse.from_orm(db_item)
    except CRUDError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put(
    "/checklists/{checklist_id}/items/{item_id}",
    response_model=schemas.ChecklistItemResponse,
    tags=["Checklist Items"],
    summary="Update Checklist Item",
    description="Update an existing checklist item"
)
async def update_checklist_item(
    checklist_id: UUID,
    item_id: UUID,
    item_update: schemas.ChecklistItemUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a checklist item."""
    try:
        db_item = crud.update_checklist_item(db, item_id, item_update, current_user.id)
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist item not found"
            )
        return schemas.ChecklistItemResponse.from_orm(db_item)
    except CRUDError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/checklists/{checklist_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Checklist Items"],
    summary="Delete Checklist Item",
    description="Remove an item from a checklist"
)
async def delete_checklist_item(
    checklist_id: UUID,
    item_id: UUID,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a checklist item."""
    try:
        deleted = crud.delete_checklist_item(db, item_id, current_user.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist item not found"
            )
        return None
    except CRUDError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch(
    "/checklists/{checklist_id}/items/{item_id}/toggle",
    response_model=schemas.ChecklistItemResponse,
    tags=["Checklist Items"],
    summary="Toggle Item Completion",
    description="Toggle the completion status of a checklist item"
)
async def toggle_checklist_item_completion(
    checklist_id: UUID,
    item_id: UUID,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Toggle checklist item completion status."""
    try:
        db_item = crud.toggle_checklist_item(db, item_id, current_user.id)
        if not db_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist item not found"
            )
        return schemas.ChecklistItemResponse.from_orm(db_item)
    except CRUDError as e:
        raise HTTPException(status_code=500, detail=str(e))


# Import time for request logging
import time


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )