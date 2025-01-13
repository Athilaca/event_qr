from fastapi import FastAPI, Form, UploadFile, Depends
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, Base, get_db
import shutil
import os

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

PROFILE_PIC_DIR = "profile_pictures"
os.makedirs(PROFILE_PIC_DIR, exist_ok=True)

@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(
    name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    profile_picture: UploadFile = None,
    db: Session = Depends(get_db),
):
    # Handle profile picture upload
    profile_picture_path = None
    if profile_picture:
        file_path = os.path.join(PROFILE_PIC_DIR, profile_picture.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(profile_picture.file, f)
        profile_picture_path = file_path

    # Create user data dictionary
    user_data = {
        "name": name,
        "email": email,
        "phone_number": phone_number,
        "profile_picture": profile_picture_path,
    }

    # Create user
    return crud.create_user(db, user_data)
