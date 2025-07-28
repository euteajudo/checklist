"""
Pydantic schemas for request/response validation and serialization.

This module defines the data validation schemas used by FastAPI endpoints.
Schemas handle request validation, response serialization, and data transformation.
"""

from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from typing import List, Optional, Literal
from uuid import UUID


# User Schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's display name")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    google_id: str = Field(..., min_length=1, description="Google account identifier")
    
    @validator('name')
    def validate_name(cls, v):
        """Ensure name is not just whitespace."""
        if v and not v.strip():
            raise ValueError('Name cannot be empty or just whitespace')
        return v.strip() if v else v


class UserResponse(UserBase):
    """Schema for user response data."""
    id: UUID = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        from_attributes = True


# Authentication Schemas
class GoogleOAuthData(BaseModel):
    """Schema for Google OAuth authentication data."""
    credential: str = Field(..., description="Google JWT credential token")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="Authenticated user data")


# Checklist Item Schemas
class ChecklistItemBase(BaseModel):
    """Base checklist item schema with common fields."""
    description: str = Field(..., min_length=1, max_length=1000, description="Item description")
    priority: Optional[Literal["low", "medium", "high"]] = Field(
        default="medium", 
        description="Item priority level"
    )
    due_date: Optional[datetime] = Field(None, description="Optional due date")
    
    @validator('description')
    def validate_description(cls, v):
        """Ensure description is not just whitespace."""
        if not v.strip():
            raise ValueError('Description cannot be empty or just whitespace')
        return v.strip()


class ChecklistItemCreate(ChecklistItemBase):
    """Schema for creating a new checklist item."""
    display_order: Optional[int] = Field(default=0, ge=0, description="Display order")


class ChecklistItemUpdate(BaseModel):
    """Schema for updating an existing checklist item."""
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    is_completed: Optional[bool] = Field(None, description="Completion status")
    priority: Optional[Literal["low", "medium", "high"]] = Field(None)
    due_date: Optional[datetime] = Field(None)
    display_order: Optional[int] = Field(None, ge=0)
    
    @validator('description')
    def validate_description(cls, v):
        """Ensure description is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or just whitespace')
        return v.strip() if v else v


class ChecklistItemResponse(ChecklistItemBase):
    """Schema for checklist item response data."""
    id: UUID = Field(..., description="Item's unique identifier")
    checklist_id: UUID = Field(..., description="Parent checklist identifier")
    is_completed: bool = Field(..., description="Whether the item is completed")
    display_order: int = Field(..., description="Display order within the checklist")
    created_at: datetime = Field(..., description="Item creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    is_overdue: bool = Field(..., description="Whether the item is past its due date")
    
    class Config:
        from_attributes = True


# Checklist Schemas
class ChecklistBase(BaseModel):
    """Base checklist schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Checklist title")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")
    
    @validator('title')
    def validate_title(cls, v):
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Ensure description is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or just whitespace')
        return v.strip() if v else v


class ChecklistCreate(ChecklistBase):
    """Schema for creating a new checklist."""
    items: Optional[List[ChecklistItemCreate]] = Field(
        default_factory=list, 
        description="Initial items for the checklist"
    )
    
    @validator('items')
    def validate_items_limit(cls, v):
        """Limit the number of items that can be created at once."""
        if len(v) > 50:  # Reasonable limit
            raise ValueError('Cannot create more than 50 items at once')
        return v


class ChecklistUpdate(BaseModel):
    """Schema for updating an existing checklist."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    
    @validator('title')
    def validate_title(cls, v):
        """Ensure title is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        return v.strip() if v else v
    
    @validator('description')
    def validate_description(cls, v):
        """Ensure description is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or just whitespace')
        return v.strip() if v else v


class ChecklistResponse(ChecklistBase):
    """Schema for checklist response data."""
    id: UUID = Field(..., description="Checklist's unique identifier")
    user_id: UUID = Field(..., description="Owner's user identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    items: List[ChecklistItemResponse] = Field(default_factory=list, description="Checklist items")
    total_items: int = Field(..., description="Total number of items")
    completed_items: int = Field(..., description="Number of completed items")
    completion_percentage: float = Field(..., description="Completion percentage (0-100)")
    
    class Config:
        from_attributes = True


class ChecklistSummary(BaseModel):
    """Schema for checklist summary (without items)."""
    id: UUID = Field(..., description="Checklist's unique identifier")
    title: str = Field(..., description="Checklist title")
    description: Optional[str] = Field(None, description="Optional description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")
    total_items: int = Field(..., description="Total number of items")
    completed_items: int = Field(..., description="Number of completed items")
    completion_percentage: float = Field(..., description="Completion percentage (0-100)")
    
    class Config:
        from_attributes = True


# Toggle Item Completion Schema
class ToggleItemCompletion(BaseModel):
    """Schema for toggling item completion status."""
    is_completed: bool = Field(..., description="New completion status")


# Error Response Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")


class ValidationErrorResponse(BaseModel):
    """Schema for validation error responses."""
    detail: List[dict] = Field(..., description="List of validation errors")
    error_code: str = Field(default="validation_error", description="Error code")


# Pagination Schemas
class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of records to return")


class PaginatedResponse(BaseModel):
    """Schema for paginated responses."""
    items: List[ChecklistSummary] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum items per page")