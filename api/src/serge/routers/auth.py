from fastapi import APIRouter, Response, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from datetime import timedelta

from serge.models.user import User, Token, TokenData, AuthType, create_user, get_user
from serge.utils.security import verify_password, create_access_token, decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    match user.auth_type:
        case AuthType.USERNAMEPASS:
            if not verify_password(password, user.secret):
                return False
        case _:
            return False
    return user

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
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
    response.set_cookie(key="token", value=access_token, httponly=True, secure=True, samesite='strict')
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/logout")
async def logout(response: Response):
    # Clear the token cookie by setting it to expire immediately
    response.delete_cookie(key="token")
    return {"message": "Logged out successfully"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
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

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(request: Request) -> User:
    token = request.cookies.get('token')
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    return await get_current_user(token)