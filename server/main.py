import mimetypes
import logging
import sys
import os
import subprocess
import time
from sqlalchemy.exc import OperationalError

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse

from app import app
from constants import *
from utils import find_file
from database import init_db, get_session_factory, User
from auth_api import hash_password

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting Toolbox.io server initialization...")

# Import routes after app is defined
logger.debug("Importing route modules...")
# noinspection PyUnresolvedReferences
import routes.core
# noinspection PyUnresolvedReferences
import routes.auth_api_r
# noinspection PyUnresolvedReferences
import routes.auth
logger.debug("Route modules imported successfully")

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
        # Create database and user using mysql command
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
    try:
        db = get_session_factory()()
        # Check if test user already exists
        logger.debug("Checking if test user already exists...")
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            logger.info("Test user already exists!")
            return
        # Create test user
        logger.info("Creating test user...")
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password123")
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
        # Only initialize tables and create test user
        logger.info("Creating database tables...")
        init_db()
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

@app.get("/{path:path}")
async def serve_files(path: str, request: Request):
    """Serve .mdpage.md files first, then files from the content directory with various fallbacks."""
    mdpath = path.upper()
    
    # Log request for monitoring
    logger.info(f"Serving request: {request.method} {request.url.path} from {request.client.host}")
    
    # 1. Try to serve .mdpage.md file first
    if (CONTENT_PATH / f"{mdpath}.page.md").resolve().is_file():
        logger.info(f"Serving markdown page: {mdpath}.page.md")
        return templates.TemplateResponse(
            "mdpage.html",
            {"request": request, "file": f"{mdpath}.page.md"}
        )

    # 2. Fallback to regular file logic
    logger.debug(f"Looking up file for path: {path}")
    file_path, redirect_path = find_file(path)
    
    if redirect_path:
        # Preserve query parameters
        query_string = request.url.query
        redirect_url = redirect_path
        if query_string:
            if '?' in redirect_url:
                redirect_url += f"&{query_string}"
            else:
                redirect_url += f"?{query_string}"
        logger.info(f"Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
    
    if not file_path:
        logger.warning(f"File not found: {path}")
        raise HTTPException(status_code=404, detail="File not found")

    if file_path.is_file() and (
        file_path.name.endswith(".ts") or
        file_path.name.endswith(".scss") or
        file_path.name == "minify.sh" or
        file_path.name == "package.json" or
        file_path.name == "tsconfig.json" or
        file_path.parent.resolve() == (CONTENT_PATH / "templates").resolve()
    ):
        logger.warning(f"Access denied to: {file_path}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    mime_type, _ = mimetypes.guess_type(str(file_path))
    logger.info(f"Serving file: {file_path} (type: {mime_type})")
    return FileResponse(
        path=file_path,
        media_type=mime_type
    )

if __name__ == "__main__":
    import uvicorn
    # Initialize database before starting the server
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        sys.exit(1)
    logger.info("Starting Toolbox.io server...")
    logger.info(f"Server will run on host: 0.0.0.0, port: 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
