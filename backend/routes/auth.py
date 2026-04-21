from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from backend.core.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    get_current_user
)
from backend.core.db import users_collection, invite_codes_collection
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    invite_code: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/register")
async def register(user_in: UserRegister):
    # 1. Verify Invite Code
    code = invite_codes_collection.find_one({"code": user_in.invite_code, "used": False})
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used invitation code."
        )
    
    # 2. Check existing user
    if users_collection.find_one({"email": user_in.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    
    # 3. Create user
    user_dict = {
        "email": user_in.email,
        "hashed_password": get_password_hash(user_in.password),
        "full_name": user_in.full_name,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = users_collection.insert_one(user_dict)
    
    # 4. Mark invite code as used
    invite_codes_collection.update_one(
        {"_id": code["_id"]},
        {"$set": {"used": True, "used_by": user_in.email, "used_at": datetime.utcnow()}}
    )
    
    return {"message": "User registered successfully", "id": str(result.inserted_id)}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["email"]})
    
    # Clean user object for frontend
    user_data = {
        "id": str(user["_id"]),
        "email": user["email"],
        "full_name": user.get("full_name", "")
    }
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user_data
    }

@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    user_data = current_user.copy()
    del user_data["hashed_password"]
    return user_data
