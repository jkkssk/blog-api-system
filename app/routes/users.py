from fastapi import APIRouter, HTTPException, status
from app.database import db
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.models import User

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    for user in db.get_all_users():
        if user.email == user_data.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if user.login == user_data.login:
            raise HTTPException(status_code=400, detail="Login already taken")
    
    user_id = db.get_next_user_id()
    user = User(
        id=user_id,
        email=user_data.email,
        login=user_data.login,
        password=user_data.password
    )
    
    db.save_user(user)
    return user

@router.get("/", response_model=list[UserResponse])
async def get_all_users():
    return db.get_all_users()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate):
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.login:
        for existing_user in db.get_all_users():
            if existing_user.id != user_id and existing_user.login == user_data.login:
                raise HTTPException(status_code=400, detail="Login already taken")
    
    updated_user = db.update_user(user_id, **user_data.model_dump(exclude_unset=True))
    return updated_user

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    if not db.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}