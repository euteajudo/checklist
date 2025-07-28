"""
SQLAlchemy models for the Checklist application.

This module defines the database models for users, checklists, and checklist items.
All models inherit from the Base class defined in database.py and use UUID for primary keys.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base


class User(Base):
    """
    User model representing authenticated users in the system.
    
    Users authenticate via Google OAuth and can create multiple checklists.
    
    Attributes:
        id (UUID): Primary key, auto-generated UUID
        email (str): User's email address, unique and indexed
        name (str): User's display name from Google profile
        google_id (str): Google account identifier, unique
        created_at (datetime): Account creation timestamp
        checklists (relationship): Related Checklist objects
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    google_id = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # Relationships
    checklists = relationship(
        "Checklist", 
        back_populates="user", 
        cascade="all, delete-orphan",
        order_by="Checklist.created_at.desc()"
    )
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', name='{self.name}')>"


class Checklist(Base):
    """
    Checklist model representing a collection of tasks/items.
    
    Each checklist belongs to a user and contains multiple checklist items.
    
    Attributes:
        id (UUID): Primary key, auto-generated UUID
        user_id (UUID): Foreign key to User model
        title (str): Checklist title, required
        description (str): Optional checklist description
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last modification timestamp
        user (relationship): Related User object
        items (relationship): Related ChecklistItem objects
    """
    __tablename__ = "checklists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user = relationship("User", back_populates="checklists")
    items = relationship(
        "ChecklistItem", 
        back_populates="checklist", 
        cascade="all, delete-orphan",
        order_by="ChecklistItem.display_order.asc()"
    )
    
    # Add constraints
    __table_args__ = (
        CheckConstraint('length(title) >= 1', name='check_title_not_empty'),
    )
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage of the checklist."""
        if not self.items:
            return 0.0
        completed_items = sum(1 for item in self.items if item.is_completed)
        return (completed_items / len(self.items)) * 100
    
    @property
    def total_items(self) -> int:
        """Get total number of items in the checklist."""
        return len(self.items)
    
    @property
    def completed_items(self) -> int:
        """Get number of completed items in the checklist."""
        return sum(1 for item in self.items if item.is_completed)
    
    def __repr__(self):
        return f"<Checklist(id='{self.id}', title='{self.title}', items={self.total_items})>"


class ChecklistItem(Base):
    """
    ChecklistItem model representing individual tasks within a checklist.
    
    Each item belongs to a checklist and tracks completion status, priority, and order.
    
    Attributes:
        id (UUID): Primary key, auto-generated UUID
        checklist_id (UUID): Foreign key to Checklist model
        description (str): Item description/task, required
        is_completed (bool): Completion status, defaults to False
        priority (str): Priority level (low, medium, high)
        due_date (datetime): Optional due date for the item
        order (int): Display order within the checklist, defaults to 0
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last modification timestamp
        checklist (relationship): Related Checklist object
    """
    __tablename__ = "checklist_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    checklist_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("checklists.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    description = Column(String(1000), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    priority = Column(String(10), default="medium")  # low, medium, high
    due_date = Column(DateTime(timezone=True))
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    checklist = relationship("Checklist", back_populates="items")
    
    # Add constraints
    __table_args__ = (
        CheckConstraint('length(description) >= 1', name='check_description_not_empty'),
        CheckConstraint("priority IN ('low', 'medium', 'high')", name='check_valid_priority'),
        CheckConstraint('display_order >= 0', name='check_display_order_non_negative'),
    )
    
    @property
    def is_overdue(self) -> bool:
        """Check if the item is overdue."""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and not self.is_completed
    
    def __repr__(self):
        status = "✓" if self.is_completed else "○"
        return f"<ChecklistItem(id='{self.id}', description='{self.description[:30]}...', completed={status})>"