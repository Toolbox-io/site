from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from models import Photo, User
from db.core import get_db  # Adjust if your session dependency is elsewhere
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
    # Limit file size to 50MB, read in chunks
    MAX_SIZE = 50 * 1024 * 1024
    chunk_size = 1024 * 1024  # 1MB
    total_size = 0
    filename = f"{current_user.id}_{photo_uuid}.bin"
    file_path = os.path.join(PHOTO_DIR, filename)
    with open(file_path, "wb") as out_file:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_SIZE:
                out_file.close()
                os.remove(file_path)
                raise HTTPException(status_code=413, detail="File too large (max 50MB)")
            out_file.write(chunk)
    
    # Check if UUID already exists for this user
    existing = db.query(Photo).filter_by(uuid=photo_uuid, user_id=current_user.id).first()
    if existing:
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