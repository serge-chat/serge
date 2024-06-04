import uuid

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserAuth(UserBase):
    secret: str
    auth_type: int


class User(UserBase):
    id: uuid.UUID = uuid.uuid4()
    is_active: bool = True
    email: str = ""
    full_name: str = ""
    theme_light: bool = False
    default_prompt: str = (
        "Below is an instruction that describes a task. Write a response that appropriately completes the request."
    )
    auth: list[UserAuth] = []

    class Config:
        orm_mode = True
