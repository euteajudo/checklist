"""
CRUD operations for the Checklist application.

This module contains all database operations for users, checklists, and checklist items.
All functions include proper error handling, logging, and transaction management with rollback.
"""

import logging
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID
from typing import List, Optional, Tuple

from . import models, schemas

# Configure logging
logger = logging.getLogger(__name__)


class CRUDError(Exception):
    """Custom exception for CRUD operation errors."""
    pass


# User CRUD Operations
def get_user(db: Session, user_id: UUID) -> Optional[models.User]:
    """
    Retrieve a user by their ID.
    
    Args:
        db (Session): Database session
        user_id (UUID): User's unique identifier
        
    Returns:
        Optional[User]: User model instance if found, None otherwise
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            logger.debug(f"User retrieved successfully: {user_id}")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving user {user_id}: {str(e)}")
        raise CRUDError(f"Failed to retrieve user: {str(e)}")


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Retrieve a user by their email address.
    
    Args:
        db (Session): Database session
        email (str): User's email address
        
    Returns:
        Optional[User]: User model instance if found, None otherwise
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            logger.debug(f"User retrieved by email: {email}")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving user by email {email}: {str(e)}")
        raise CRUDError(f"Failed to retrieve user by email: {str(e)}")


def get_user_by_google_id(db: Session, google_id: str) -> Optional[models.User]:
    """
    Retrieve a user by their Google ID.
    
    Args:
        db (Session): Database session
        google_id (str): Google account identifier
        
    Returns:
        Optional[User]: User model instance if found, None otherwise
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        user = db.query(models.User).filter(models.User.google_id == google_id).first()
        if user:
            logger.debug(f"User retrieved by Google ID: {google_id}")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving user by Google ID {google_id}: {str(e)}")
        raise CRUDError(f"Failed to retrieve user by Google ID: {str(e)}")


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user in the database.
    
    Args:
        db (Session): Database session
        user (UserCreate): User creation schema with validated data
        
    Returns:
        User: Created user model instance
        
    Raises:
        CRUDError: If user creation fails or email/google_id already exists
    """
    try:
        db_user = models.User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user created successfully: {db_user.email} (ID: {db_user.id})")
        return db_user
    
    except IntegrityError as e:
        db.rollback()
        if "users_email_key" in str(e):
            logger.warning(f"Attempted to create user with existing email: {user.email}")
            raise CRUDError(f"User with email {user.email} already exists")
        elif "users_google_id_key" in str(e):
            logger.warning(f"Attempted to create user with existing Google ID: {user.google_id}")
            raise CRUDError(f"User with Google ID {user.google_id} already exists")
        else:
            logger.error(f"Integrity error creating user: {str(e)}")
            raise CRUDError(f"User creation failed: {str(e)}")
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating user: {str(e)}")
        raise CRUDError(f"Failed to create user: {str(e)}")


# Checklist CRUD Operations
def get_checklists(
    db: Session, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 100
) -> Tuple[List[models.Checklist], int]:
    """
    Retrieve user's checklists with pagination.
    
    Args:
        db (Session): Database session
        user_id (UUID): User's unique identifier
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        
    Returns:
        Tuple[List[Checklist], int]: List of checklists and total count
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        # Get checklists with eager loading of items for efficiency
        query = db.query(models.Checklist).filter(
            models.Checklist.user_id == user_id
        ).options(selectinload(models.Checklist.items))
        
        total = query.count()
        checklists = query.offset(skip).limit(limit).all()
        
        logger.debug(f"Retrieved {len(checklists)} checklists for user {user_id} (total: {total})")
        return checklists, total
    
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving checklists for user {user_id}: {str(e)}")
        raise CRUDError(f"Failed to retrieve checklists: {str(e)}")


def get_checklist(db: Session, checklist_id: UUID, user_id: UUID) -> Optional[models.Checklist]:
    """
    Retrieve a specific checklist belonging to a user.
    
    Args:
        db (Session): Database session
        checklist_id (UUID): Checklist's unique identifier
        user_id (UUID): User's unique identifier
        
    Returns:
        Optional[Checklist]: Checklist model instance if found and owned by user
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        checklist = db.query(models.Checklist).filter(
            models.Checklist.id == checklist_id,
            models.Checklist.user_id == user_id
        ).options(selectinload(models.Checklist.items)).first()
        
        if checklist:
            logger.debug(f"Checklist retrieved: {checklist_id} for user {user_id}")
        else:
            logger.debug(f"Checklist not found or access denied: {checklist_id} for user {user_id}")
        
        return checklist
    
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving checklist {checklist_id}: {str(e)}")
        raise CRUDError(f"Failed to retrieve checklist: {str(e)}")


def create_checklist(db: Session, checklist: schemas.ChecklistCreate, user_id: UUID) -> models.Checklist:
    """
    Create a new checklist with initial items.
    
    Args:
        db (Session): Database session
        checklist (ChecklistCreate): Checklist creation schema
        user_id (UUID): Owner's user identifier
        
    Returns:
        Checklist: Created checklist model instance
        
    Raises:
        CRUDError: If checklist creation fails
    """
    try:
        # Extract items data and create checklist
        checklist_data = checklist.dict()
        items_data = checklist_data.pop('items', [])
        
        db_checklist = models.Checklist(**checklist_data, user_id=user_id)
        db.add(db_checklist)
        db.flush()  # Get the checklist ID without committing
        
        # Create initial items if provided
        for idx, item_data in enumerate(items_data):
            db_item = models.ChecklistItem(
                **item_data,
                checklist_id=db_checklist.id,
                display_order=idx
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_checklist)
        
        logger.info(
            f"Checklist created successfully: {db_checklist.id} "
            f"with {len(items_data)} items for user {user_id}"
        )
        return db_checklist
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating checklist for user {user_id}: {str(e)}")
        raise CRUDError(f"Failed to create checklist: {str(e)}")


def update_checklist(
    db: Session, 
    checklist_id: UUID, 
    checklist: schemas.ChecklistUpdate, 
    user_id: UUID
) -> Optional[models.Checklist]:
    """
    Update an existing checklist.
    
    Args:
        db (Session): Database session
        checklist_id (UUID): Checklist's unique identifier
        checklist (ChecklistUpdate): Update data
        user_id (UUID): User's unique identifier
        
    Returns:
        Optional[Checklist]: Updated checklist if found and updated successfully
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        db_checklist = get_checklist(db, checklist_id, user_id)
        if not db_checklist:
            logger.warning(f"Checklist not found for update: {checklist_id} (user: {user_id})")
            return None
        
        update_data = checklist.dict(exclude_unset=True)
        if not update_data:
            logger.debug(f"No update data provided for checklist: {checklist_id}")
            return db_checklist
        
        for field, value in update_data.items():
            setattr(db_checklist, field, value)
        
        db.commit()
        db.refresh(db_checklist)
        
        logger.info(f"Checklist updated successfully: {checklist_id}")
        return db_checklist
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating checklist {checklist_id}: {str(e)}")
        raise CRUDError(f"Failed to update checklist: {str(e)}")


def delete_checklist(db: Session, checklist_id: UUID, user_id: UUID) -> bool:
    """
    Delete a checklist and all its items.
    
    Args:
        db (Session): Database session
        checklist_id (UUID): Checklist's unique identifier
        user_id (UUID): User's unique identifier
        
    Returns:
        bool: True if deleted successfully, False if not found
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        db_checklist = get_checklist(db, checklist_id, user_id)
        if not db_checklist:
            logger.warning(f"Checklist not found for deletion: {checklist_id} (user: {user_id})")
            return False
        
        items_count = len(db_checklist.items)
        db.delete(db_checklist)
        db.commit()
        
        logger.info(
            f"Checklist deleted successfully: {checklist_id} "
            f"(with {items_count} items) for user {user_id}"
        )
        return True
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting checklist {checklist_id}: {str(e)}")
        raise CRUDError(f"Failed to delete checklist: {str(e)}")


# ChecklistItem CRUD Operations
def create_checklist_item(
    db: Session, 
    item: schemas.ChecklistItemCreate, 
    checklist_id: UUID, 
    user_id: UUID
) -> Optional[models.ChecklistItem]:
    """
    Create a new checklist item.
    
    Args:
        db (Session): Database session
        item (ChecklistItemCreate): Item creation schema
        checklist_id (UUID): Parent checklist identifier
        user_id (UUID): User's unique identifier (for permission check)
        
    Returns:
        Optional[ChecklistItem]: Created item if successful, None if checklist not found
        
    Raises:
        CRUDError: If item creation fails
    """
    try:
        # Verify user owns the checklist
        checklist = get_checklist(db, checklist_id, user_id)
        if not checklist:
            logger.warning(f"Attempted to add item to non-existent checklist: {checklist_id}")
            return None
        
        db_item = models.ChecklistItem(**item.dict(), checklist_id=checklist_id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        logger.info(f"Checklist item created: {db_item.id} in checklist {checklist_id}")
        return db_item
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating checklist item: {str(e)}")
        raise CRUDError(f"Failed to create checklist item: {str(e)}")


def update_checklist_item(
    db: Session, 
    item_id: UUID, 
    item: schemas.ChecklistItemUpdate,
    user_id: UUID
) -> Optional[models.ChecklistItem]:
    """
    Update an existing checklist item.
    
    Args:
        db (Session): Database session
        item_id (UUID): Item's unique identifier
        item (ChecklistItemUpdate): Update data
        user_id (UUID): User's unique identifier (for permission check)
        
    Returns:
        Optional[ChecklistItem]: Updated item if found and updated successfully
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        # Get item with checklist to verify ownership
        db_item = db.query(models.ChecklistItem).join(
            models.Checklist
        ).filter(
            models.ChecklistItem.id == item_id,
            models.Checklist.user_id == user_id
        ).first()
        
        if not db_item:
            logger.warning(f"Checklist item not found or access denied: {item_id} (user: {user_id})")
            return None
        
        update_data = item.dict(exclude_unset=True)
        if not update_data:
            logger.debug(f"No update data provided for item: {item_id}")
            return db_item
        
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        
        logger.info(f"Checklist item updated: {item_id}")
        return db_item
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating checklist item {item_id}: {str(e)}")
        raise CRUDError(f"Failed to update checklist item: {str(e)}")


def delete_checklist_item(db: Session, item_id: UUID, user_id: UUID) -> bool:
    """
    Delete a checklist item.
    
    Args:
        db (Session): Database session
        item_id (UUID): Item's unique identifier
        user_id (UUID): User's unique identifier (for permission check)
        
    Returns:
        bool: True if deleted successfully, False if not found
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        # Get item with checklist to verify ownership
        db_item = db.query(models.ChecklistItem).join(
            models.Checklist
        ).filter(
            models.ChecklistItem.id == item_id,
            models.Checklist.user_id == user_id
        ).first()
        
        if not db_item:
            logger.warning(f"Checklist item not found or access denied: {item_id} (user: {user_id})")
            return False
        
        db.delete(db_item)
        db.commit()
        
        logger.info(f"Checklist item deleted: {item_id}")
        return True
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting checklist item {item_id}: {str(e)}")
        raise CRUDError(f"Failed to delete checklist item: {str(e)}")


def toggle_checklist_item(db: Session, item_id: UUID, user_id: UUID) -> Optional[models.ChecklistItem]:
    """
    Toggle the completion status of a checklist item.
    
    Args:
        db (Session): Database session
        item_id (UUID): Item's unique identifier
        user_id (UUID): User's unique identifier (for permission check)
        
    Returns:
        Optional[ChecklistItem]: Updated item if found and toggled successfully
        
    Raises:
        CRUDError: If database operation fails
    """
    try:
        # Get item with checklist to verify ownership
        db_item = db.query(models.ChecklistItem).join(
            models.Checklist
        ).filter(
            models.ChecklistItem.id == item_id,
            models.Checklist.user_id == user_id
        ).first()
        
        if not db_item:
            logger.warning(f"Checklist item not found or access denied: {item_id} (user: {user_id})")
            return None
        
        old_status = db_item.is_completed
        db_item.is_completed = not db_item.is_completed
        db.commit()
        db.refresh(db_item)
        
        logger.info(
            f"Checklist item toggled: {item_id} "
            f"({old_status} -> {db_item.is_completed})"
        )
        return db_item
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error toggling checklist item {item_id}: {str(e)}")
        raise CRUDError(f"Failed to toggle checklist item: {str(e)}")