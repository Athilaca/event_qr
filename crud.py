import os
import qrcode
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import User

QR_CODE_DIR = "qrcodes"
os.makedirs(QR_CODE_DIR, exist_ok=True)

def generate_qr_code(data: str, filename: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img_path = os.path.join(QR_CODE_DIR, filename)
    img.save(img_path)
    return img_path

def create_user(db: Session, user_data: dict):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user_data["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    # Create the user and add to database
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate QR code
    qr_data = f"Name: {user.name}\nEmail: {user.email}\nPhone: {user.phone_number}"
    qr_code_path = generate_qr_code(qr_data, f"{user.id}_qr.png")

    # Update user with QR code path
    user.qr_code_path = qr_code_path
    db.commit()
    db.refresh(user)
    return user


def mark_user_as_registered(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_entered:
        raise HTTPException(status_code=400, detail="User has already entered")

    # Mark as entered
    user.is_entered = True
    db.commit()
    return {"message": "Entry marked as successful", "user": user}


