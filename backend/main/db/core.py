import logging
import os
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
ENV = os.getenv('ENV', 'development')
DB_HOST = os.getenv('DB_HOST', '0.0.0.0')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'toolbox_user')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'toolbox_db')

# Create database URL based on environment
if ENV == 'production':
    # MySQL for production
    if not DB_PASSWORD:
        logger.critical("No password")
        exit(1)
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # SQLite for development
    import os
    os.makedirs('data', exist_ok=True)
    DATABASE_URL = "sqlite:///./data/toolbox_dev.db"

logger.info(f"Initializing database with URL: {DATABASE_URL.replace(DB_PASSWORD or '', '***')}")

def create_engine_with_retry(max_retries=5, retry_delay=5):
    """Create database engine with retry mechanism"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})")
            
            # Configure engine based on database type
            if ENV == 'production':
                # MySQL configuration
                engine = create_engine(
                    DATABASE_URL,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    echo=False,  # Set to True for SQL debugging
                    connect_args={
                        "connect_timeout": 10,
                        "read_timeout": 30,
                        "write_timeout": 30
                    }
                )
            else:
                # SQLite configuration
                engine = create_engine(
                    DATABASE_URL,
                    echo=False,  # Set to True for SQL debugging
                    connect_args={"check_same_thread": False}
                )
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connection successful!")
            return engine
            
        except OperationalError as e:
            if attempt > 3:
                logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                if attempt > 3:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to connect to database after all retries")
                raise
    
    raise Exception("Failed to create database engine")

# Global variables for engine and session factory
_engine = None
_SessionLocal = None

def get_engine():
    """Get or create database engine"""
    global _engine
    if _engine is None:
        _engine = create_engine_with_retry()
    return _engine

def get_session_factory():
    """Get or create session factory"""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal

def get_db():
    """Get database session"""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close() 