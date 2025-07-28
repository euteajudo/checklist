"""
Authentication module for Google OAuth and JWT token management.

This module handles Google OAuth authentication, JWT token generation and validation,
and provides middleware for protecting routes that require authentication.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import JWTError, jwt
from passlib.context import CryptContext

from .database import get_db
from . import models, schemas, crud

# Configure logging
logger = logging.getLogger(__name__)

# Security configurations
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT and OAuth settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not GOOGLE_CLIENT_ID:
    logger.warning("GOOGLE_CLIENT_ID not found in environment variables")


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data (dict): The data to encode in the token (usually user info)
        expires_delta (timedelta, optional): Token expiration time
        
    Returns:
        str: Encoded JWT token
        
    Raises:
        AuthenticationError: If token creation fails
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    except Exception as e:
        logger.error(f"Failed to create access token: {str(e)}")
        raise AuthenticationError(f"Token creation failed: {str(e)}")


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token (str): The JWT token to verify
        
    Returns:
        dict: The decoded token payload
        
    Raises:
        AuthenticationError: If token verification fails
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            logger.warning("Token missing 'sub' claim")
            raise AuthenticationError("Invalid token: missing user ID")
        
        return payload
    
    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise AuthenticationError(f"Token verification failed: {str(e)}")


async def verify_google_token(credential: str) -> dict:
    """
    Verify Google OAuth ID token.
    
    Args:
        credential (str): Google ID token from frontend
        
    Returns:
        dict: User information from Google
        
    Raises:
        AuthenticationError: If Google token verification fails
    """
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            credential, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            logger.warning(f"Invalid token issuer: {idinfo['iss']}")
            raise AuthenticationError("Invalid token issuer")
        
        logger.info(f"Google token verified for user: {idinfo.get('email', 'unknown')}")
        
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', '')
        }
    
    except ValueError as e:
        logger.error(f"Google token verification failed: {str(e)}")
        raise AuthenticationError(f"Invalid Google token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during Google token verification: {str(e)}")
        raise AuthenticationError(f"Google token verification failed: {str(e)}")


async def authenticate_google_user(
    google_data: schemas.GoogleOAuthData, 
    db: Session
) -> schemas.TokenResponse:
    """
    Authenticate user with Google OAuth and return JWT token.
    
    Args:
        google_data (GoogleOAuthData): Google OAuth credential data
        db (Session): Database session
        
    Returns:
        TokenResponse: JWT token and user data
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify Google token
        user_info = await verify_google_token(google_data.credential)
        
        # Check if user already exists
        db_user = crud.get_user_by_google_id(db, user_info['google_id'])
        
        if not db_user:
            # Create new user
            user_create = schemas.UserCreate(
                email=user_info['email'],
                name=user_info['name'],
                google_id=user_info['google_id']
            )
            db_user = crud.create_user(db, user_create)
            logger.info(f"New user created: {db_user.email}")
        else:
            # Update user info if needed
            if db_user.name != user_info['name'] or db_user.email != user_info['email']:
                db_user.name = user_info['name']
                db_user.email = user_info['email']
                db.commit()
                logger.info(f"User info updated: {db_user.email}")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(db_user.id), "email": db_user.email}
        )
        
        # Convert to response schema
        user_response = schemas.UserResponse.from_orm(db_user)
        
        return schemas.TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
    
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error during authentication: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during authentication"
        )
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get the current authenticated user from JWT token.
    
    This dependency function extracts and validates the JWT token from the
    Authorization header and returns the corresponding user from the database.
    
    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from request header
        db (Session): Database session dependency
        
    Returns:
        User: The authenticated user model instance
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        payload = verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            logger.warning("Token missing user ID")
            raise credentials_exception
        
        # Get user from database
        user = crud.get_user(db, user_id=user_id)
        if user is None:
            logger.warning(f"User not found in database: {user_id}")
            raise credentials_exception
        
        return user
    
    except AuthenticationError:
        logger.warning("Token verification failed")
        raise credentials_exception
    except SQLAlchemyError as e:
        logger.error(f"Database error during user lookup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    except Exception as e:
        logger.error(f"Unexpected error during user authentication: {str(e)}")
        raise credentials_exception


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Get the current active user (additional checks can be added here).
    
    Args:
        current_user (User): Current authenticated user
        
    Returns:
        User: The active user
        
    Raises:
        HTTPException: If user is not active (can be extended)
    """
    # Here you could add additional checks like:
    # - User account is not disabled
    # - User has verified email
    # - User subscription is active
    # etc.
    
    return current_user