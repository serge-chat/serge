from enum import Enum
from pydantic import BaseModel
from typing import Optional, Literal

from redis import Redis
from serge.utils.security import get_password_hash

class AuthType(Enum):
    USERNAMEPASS = 1

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    pref_theme: Literal["light", "dark"] = "dark"
    default_prompt: str = "Below is an instruction that describes a task. Write a response that assists {full_name} appropriately completes the request."


class DBUser(User):
    auth_type: AuthType
    secret: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


def get_user(username: str) -> DBUser | None:
    client = Redis(host="localhost", port=6379, decode_responses=False)
    if not client.sismember("users", username):
        return None

    user_raw = client.get(f"user:{username}")
    user = DBUser.parse_raw(user_raw)
    return user

def create_user(userdata: DBUser) -> None:
    client = Redis(host="localhost", port=6379, decode_responses=False)
    match userdata.auth_type:
        case AuthType.USERNAMEPASS:
            userdata.secret = get_password_hash(userdata.secret)
        case _:
            pass
    client.sadd("users", userdata.username)
    client.set(f"user:{userdata.username}", userdata.json())

def update_user(userdata: User):
    client = Redis(host="localhost", port=6379, decode_responses=False)
    client.set(f"user:{userdata.username}", userdata.json())
