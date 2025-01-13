from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas

router = APIRouter()

@router.post("/register/")
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Call the CRUD function to register the user
    user_data = user.dict()
    new_user = crud.create_user(db, user_data)
    return {"message": "Registration successful", "user_id": new_user.id, "qr_code_path": new_user.qr_code_path}

@router.post("/scan-qr/{user_id}")
async def scan_qr(user_id: int, db: Session = Depends(get_db)):
    # Mark the user as registered when their QR code is scanned
    updated_user = crud.mark_user_as_registered(db, user_id)
    return {"message": "User registration confirmed", "user": updated_user}
