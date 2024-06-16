import logging
import uuid
from typing import List, Optional

from serge.schema import user as user_schema
from serge.utils.security import get_password_hash
from sqlalchemy.orm import Session

from serge.models import user as user_model


def get_user(db: Session, username: str) -> Optional[user_schema.User]:
    return Mappers.user_db_to_view(
        db.query(user_model.User).filter(user_model.User.username == username).first(),
        include_auth=True,
    )


def get_user_by_email(db: Session, email: str) -> Optional[user_schema.User]:
    return Mappers.user_db_to_view(db.query(user_model.User).filter(user_model.User.email == email).first())


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[user_schema.User]:
    return [Mappers.user_db_to_view(u) for u in db.query(user_model.User).offset(skip).limit(limit).all()]


def create_user(db: Session, ua: user_schema.UserAuth) -> Optional[user_schema.User]:
    # Check already exists
    if get_user(db, ua.username):
        logging.error(f"Tried to create new user, but already exists: {ua.username}")
        return None

    match ua.auth_type:
        case 1:
            ua.secret = get_password_hash(ua.secret)
        case _:  # Todo: More auth types
            return None

    db_user, db_user_auth = Mappers.user_view_to_db(None, ua)
    db.add(db_user_auth)
    db.add(db_user)
    db.commit()
    return Mappers.user_db_to_view(db_user)


def create_chat(db: Session, chat: user_schema.Chat):
    c = user_model.Chat(owner=chat.owner, chat_id=chat.chat_id)
    db.add(c)
    db.commit()


def update_user(db: Session, u: user_schema.User) -> Optional[user_schema.User]:
    user = db.query(user_model.User).filter(user_model.User.username == u.username).first()
    if not user:
        return None
    for k, v in u.dict().items():
        if k in ["auth", "chats"]:
            continue
        setattr(user, k, v)
    db.commit()
    return user


class Mappers:
    @staticmethod
    def user_db_to_view(u: user_model.User, include_auth=False) -> user_schema.User:
        if not u:
            return None
        auths = chats = []
        if include_auth:
            auths = u.auth
        # u.auth = []
        chats = u.chats
        # u.chats = []
        app_user = user_schema.User(**{k: v for k, v in u.__dict__.items() if not k.startswith("_") and k not in ["chats", "auth"]})

        app_user.auth = [user_schema.UserAuth(username=u.username, secret=x.secret, auth_type=x.auth_type) for x in auths]

        app_user.chats = [user_schema.Chat(chat_id=x.chat_id, owner=x.owner) for x in chats]

        return app_user

    @staticmethod
    def user_view_to_db(
        u: Optional[user_schema.User] = None, ua: Optional[user_schema.UserAuth] = None
    ) -> (user_model.User, Optional[user_model.UserAuth]):
        assert u or ua, "One of User or UserAuth must be passed"
        if not u:  # Creating a new user
            u = user_schema.User(id=uuid.uuid4(), username=ua.username)
        auth = []
        if ua:
            auth = Mappers.user_auth_view_to_db(ua, u.id)
        user = user_model.User(**u.dict())
        if auth:
            user.auth.append(auth)
        for chat in u.chats:
            user.chats.append(user_model.Chat(chat_id=chat.chat_id))
        return (user, auth)

    @staticmethod
    def user_auth_view_to_db(ua: user_schema.UserAuth, user_id: uuid.UUID) -> user_model.UserAuth:
        if not ua:
            return None
        return user_model.UserAuth(secret=ua.secret, auth_type=ua.auth_type, user_id=user_id)
