from typing import Annotated

from fastapi import APIRouter, Depends, Form

from serge.routers.auth import get_current_active_user
from serge.models.user import DBUser, User, AuthType, create_user, update_user

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@user_router.get("/", response_model=User)
async def get_user(u: User = Depends(get_current_active_user)):
    if not u:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return u

@user_router.post("/create", response_model=User)
async def create_user_with_pass(u: DBUser):
    create_user(u)
    return u

@user_router.put("/", response_model=User)
async def self_update_user(new_data: User, current: User = Depends(get_current_active_user)):
    current.email = new_data.email
    current.full_name = new_data.full_name
    current.default_prompt = new_data.default_prompt
    update_user(current)
    return current
