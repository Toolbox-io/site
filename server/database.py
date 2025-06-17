import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Configure logging
logger = logging.getLogger(__name__)

# Ensure the data directory exists before initializing the database
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

# Database setup
DATABASE_URL = "sqlite:///./data/users.db"
logger.info(f"Initializing database with URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

# Create tables
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

def get_db():
    """Get database session with logging"""
    logger.debug("Creating new database session")
    db = SessionLocal()
    try:
        logger.debug("Database session created successfully")
        yield db
    except Exception as e:
        logger.error(f"Error in database session: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        db.close() 