from datetime import timedelta

from fastapi import (APIRouter, Depends, HTTPException, Request, Response,
                     status)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from serge.crud import get_user
from serge.database import SessionLocal
from serge.models.user import Token, User
from serge.utils.security import (create_access_token, decode_access_token,
                                  verify_password)
from sqlalchemy.orm import Session

from serge.models import user as user_schema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(db, username)
    if not user:
        return False
    # Users may have multipe ways to authenticate
    auths = [a.auth_type for a in user.auth]
    if 0 in auths:  # Password auth
        secret = [x for x in user.auth if x.auth_type == 0][0].secret
        if verify_password(password, secret):
            return user
    if 1 in auths:  # todo future auths
        pass
    return False


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="token", value=access_token, httponly=True, secure=True, samesite="strict"
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/logout")
async def logout(response: Response):
    # Clear the token cookie by setting it to expire immediately
    response.delete_cookie(key="token")
    return {"message": "Logged out successfully"}


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = decode_access_token(token)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(db, username)

    if user is None:
        raise credentials_exception
    # Map db model onto view model
    user.auth = []
    app_user = user_schema.User(
        **{k: v for k, v in user.__dict__.items() if not k.startswith("_")}
    )
    return app_user


async def get_current_active_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    return await get_current_user(token, db)
