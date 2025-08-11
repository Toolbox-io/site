from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from utils import FileTooLargeError, save_file
from models import Photo, User
from db.core import get_db
from routes.auth.utils import get_current_user
from limiter import limiter
from fastapi import Request
import logging

router = APIRouter()
PHOTO_DIR = "data/photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_SIZE = 50 * 1024 * 1024 # 50MB
USER_MAX_STORAGE = 1024 * 1024 * 1024  # 1GB

def get_used_storage(photos: list[Photo]):
    user_storage = 0
    for p in photos:
        try:
            if os.path.exists(p.filename):
                user_storage += os.path.getsize(p.filename)
        except Exception as e:
            logger.error(e);
            pass
    return user_storage
    

def delete_old_photos(usedStorage: int, photos: list[Photo], db: Session):
    while usedStorage > USER_MAX_STORAGE and photos:
        oldest = photos.pop(0)
        try:
            if os.path.exists(oldest.filename):
                user_storage -= os.path.getsize(oldest.filename)
                os.remove(oldest.filename)
            db.delete(oldest)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to delete old photo {oldest.uuid}: {e}")

@router.get("/sync")
def sync_photos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    photos = db.query(Photo).filter_by(user_id=current_user.id).all()
    photos_new = photos.copy()

    for photo in photos:
        logger.info(f"Checking {photo}")
        if os.path.exists(photo.filename):
            photos_new += {
                "uuid": photo.uuid, 
                "uploaded_at": photo.uploaded_at, 
                "filename": photo.filename
            }
        else:
            logger.warning(f"Photo {photo.uuid} doesn't exist")

    return {"photos": photos_new}

@router.post("/upload", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
async def upload_photo(
    request: Request,
    photo_uuid: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filename = f"{current_user.id}_{photo_uuid}.bin"
    file_path = os.path.join(PHOTO_DIR, filename)

    # Calculate current user storage usage
    user_photos = db.query(Photo).filter_by(user_id=current_user.id).order_by(Photo.uploaded_at).all()
    user_storage = get_used_storage()
    
    # Read file in chunks, check size
    try:
        total_size = save_file(input=file, output=file_path, max_size=MAX_SIZE)
    except FileTooLargeError:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")
    
    # Enforce 1GB per-user storage limit
    delete_old_photos(usedStorage=user_storage + total_size, photos=user_photos, db=db)

    # Check if UUID already exists for this user
    if db.query(Photo).filter_by(uuid=photo_uuid, user_id=current_user.id).first():
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Photo UUID already exists.")
    # Save metadata, including user_id and uuid (attached server-side)
    photo = Photo(uuid=photo_uuid, user_id=current_user.id, filename=filename)
    db.add(photo)
    db.commit()
    return {"status": "success"}

@router.get("/download/{photo_uuid}")
def download_photo(
    photo_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    photo = db.query(Photo).filter_by(uuid=photo_uuid, user_id=current_user.id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    file_path = os.path.join(PHOTO_DIR, photo.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server.")
    return FileResponse(file_path, media_type="application/octet-stream", filename=photo.filename)