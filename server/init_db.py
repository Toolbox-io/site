#!/usr/bin/env python3
"""
Database initialization script for Toolbox.io
Creates a test user for development purposes
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User
from auth_api import hash_password

def create_test_user():
    """Create a test user if it doesn't exist"""
    logger.info("Starting database initialization...")
    db = SessionLocal()
    try:
        # Check if test user already exists
        logger.debug("Checking if test user already exists...")
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            logger.info("Test user already exists!")
            return
        
        # Create test user
        logger.debug("Creating test user...")
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password123")
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        logger.info("Test user created successfully!")
        logger.info("Username: testuser")
        logger.info("Password: password123")
        logger.info("Email: test@example.com")
        logger.info(f"User ID: {test_user.id}")
        
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Initializing Toolbox.io database...")
    create_test_user()
    logger.info("Database initialization complete!") 