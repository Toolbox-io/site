import os
import time
import logging
import subprocess
from sqlalchemy.exc import OperationalError

from db.core import get_engine, get_session_factory
from routes.auth.utils import hash_password
from models import User, Base

logger = logging.getLogger(__name__)

def is_mysql_running():
    """Check if MySQL is already running"""
    try:
        result = subprocess.run(
            ['mysqladmin', 'ping', '-h', 'localhost'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def wait_for_mysql():
    """Wait for MySQL to be ready"""
    logger.info("Waiting for MySQL to be ready...")
    max_attempts = 30
    attempt = 0
    while attempt < max_attempts:
        try:
            result = subprocess.run(
                ['mysqladmin', 'ping', '-h', 'localhost'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("MySQL is ready!")
                return True
        except FileNotFoundError:
            logger.error("mysqladmin not found. Make sure MySQL is installed.")
            return False
        attempt += 1
        time.sleep(2)
        logger.info(f"Waiting for MySQL... (attempt {attempt}/{max_attempts})")
    logger.error("MySQL failed to start within expected time")
    return False

def create_database_and_user():
    """Create MySQL database and user"""
    try:
        logger.info("Setting up database and user...")
        db_password = os.getenv("DB_PASSWORD")
        sql_commands = [
            "CREATE DATABASE IF NOT EXISTS toolbox_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
            f"CREATE USER IF NOT EXISTS 'toolbox_user'@'%' IDENTIFIED BY '{db_password}';",
            "GRANT ALL PRIVILEGES ON toolbox_db.* TO 'toolbox_user'@'%';",
            f"CREATE USER IF NOT EXISTS 'toolbox_local'@'localhost' IDENTIFIED BY '{db_password}';",
            "GRANT ALL PRIVILEGES ON toolbox_db.* TO 'toolbox_local'@'localhost';",
            "FLUSH PRIVILEGES;"
        ]
        for command in sql_commands:
            result = subprocess.run(
                ['mysql', '-e', command],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error(f"Failed to execute: {command}")
                logger.error(f"Error: {result.stderr}")
                return False
        logger.info("Database and user created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating database and user: {e}")
        return False

def create_test_user():
    """Create a test user if it doesn't exist"""

    db = get_session_factory()()

    try:
        logger.debug("Checking if test user already exists...")
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            logger.info("Test user already exists!")
            return
        logger.info("Creating test user...")
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password123"),
            is_verified=True
        )
        db.add(test_user)
        db.commit()
        logger.info("Test user created successfully!")
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def initialize_database():
    """Initialize the database and create test user"""
    try:
        logger.info("Initializing Toolbox.io database...")
        logger.info("Creating database tables...")
        init_tables()
        create_test_user()
        logger.info("Database initialization complete!")
        return True
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        logger.error("Make sure MySQL server is running and accessible")
        return False
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def init_tables():
    """Initialize the database tables"""
    try:
        logger.info("Creating database tables...")
        engine = get_engine()
        # This will now create all tables registered with the Base from models.py
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise