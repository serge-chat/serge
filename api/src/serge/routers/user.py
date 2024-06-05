from fastapi import APIRouter, Depends, HTTPException, status
from serge.crud import create_user, update_user
from serge.database import SessionLocal
from serge.routers.auth import get_current_active_user
from serge.schema import user as user_schema
from sqlalchemy.orm import Session

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@user_router.get("/", response_model=user_schema.User)
async def get_user(u: user_schema.User = Depends(get_current_active_user)):
    if not u:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return u


@user_router.post("/create", response_model=user_schema.User)
async def create_user_with_pass(
    ua: user_schema.UserAuth, db: Session = Depends(get_db)
):
    try:
        u = create_user(db, ua)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to create. Username exists",
        )
    if not u:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Could not create user",
        )
    return u


@user_router.put("/", response_model=user_schema.User)
async def self_update_user(
    new_data: user_schema.User,
    current: user_schema.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    current.email = new_data.email
    current.full_name = new_data.full_name
    current.default_prompt = new_data.default_prompt
    update_user(db, current)
    return current
