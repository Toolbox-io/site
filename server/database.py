import logging
import os
import time

from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_HOST = os.getenv('DB_HOST', '95.165.0.162')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'toolbox_user')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'toolbox_db')

if not DB_PASSWORD:
    logger.critical("No password")
    exit(1)

# Create MySQL connection string
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger.info(f"Initializing database with URL: {DATABASE_URL.replace(DB_PASSWORD, '***')}")

def create_engine_with_retry(max_retries=5, retry_delay=2):
    """Create database engine with retry mechanism"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})")
            
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
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connection successful!")
            return engine
            
        except OperationalError as e:
            logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
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

# Create base class
Base = declarative_base()

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(512), unique=True, nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())

def init_db():
    """Initialize the database tables"""
    try:
        logger.info("Creating database tables...")
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

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