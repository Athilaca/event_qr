from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: str

class UserCreate(UserBase):
    profile_picture: Optional[str]  # For file upload

class UserResponse(UserBase):
    id: int
    profile_picture: Optional[str]
    qr_code_path: Optional[str]
    is_entered: bool

    class Config:
        orm_mode = True
