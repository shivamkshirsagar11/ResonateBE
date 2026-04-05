from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from app.schemas import UserLogin
from app.auth.utils import verify_password, create_access_token
from app.schemas import UserCreate, UserOut
from app.db.mongo import db
from app.auth.utils import hash_password
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.post("/signup", response_model=UserOut)
async def signup(user: UserCreate):
    users_collection = db["users"]

    # normalize username
    username = user.username.lower()

    # check existing user
    existing_user = await users_collection.find_one({
        "$or": [
            {"username": username},
            {"email": user.email}
        ]
    })

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    # create user
    new_user = {
        "username": username,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "created_at": datetime.now(timezone.utc)
    }

    await users_collection.insert_one(new_user)

    return {
        "username": username,
        "email": user.email,
        "created_at": new_user["created_at"]
    }
    
@router.post("/login")
async def login(user: UserLogin):
    users_collection = db["users"]

    username = user.username.lower()

    existing_user = await users_collection.find_one({"username": username})

    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, existing_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    return {"user": current_user}