from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from models import Photo, User
from db.core import get_db  # Adjust if your session dependency is elsewhere
from routes.auth.utils import get_current_user

router = APIRouter()
PHOTO_DIR = "photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

# TODO photo endpoints

@router.get("/sync")
def sync_photos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    photos = db.query(Photo).filter_by(user_id=current_user.id).all()
    return {
        "photos": [
            {"uuid": p.uuid, "uploaded_at": p.uploaded_at, "filename": p.filename} for p in photos
        ]
    }

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_photo(
    photo_uuid: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if UUID already exists for this user
    existing = db.query(Photo).filter_by(uuid=photo_uuid, user_id=current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Photo UUID already exists.")

    # Save encrypted file
    filename = f"{current_user.id}_{photo_uuid}.bin"
    file_path = os.path.join(PHOTO_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Save metadata, including user_id and uuid (attached server-side)
    photo = Photo(uuid=photo_uuid, user_id=current_user.id, filename=filename, encrypted=True)
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