from typing import Annotated

from fastapi import APIRouter, Depends, Form

from serge.routers.auth import get_current_active_user
from serge.models.user import DBUser, User, AuthType, create_user, update_user

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@user_router.get("/", response_model=User)
async def read_users_me(u: User = Depends(get_current_active_user)):
    return u

@user_router.post("/create", response_model=User)
async def create_user_with_pass(u: DBUser):
    create_user(u)
    return u

@user_router.put("/", response_model=User)
async def update_user(u: User = Depends(get_current_active_user)):
    update_user(u)
    return u
