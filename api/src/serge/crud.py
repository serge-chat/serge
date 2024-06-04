from typing import List, Optional

from serge.schema import user as user_schema
from serge.utils.security import get_password_hash
from sqlalchemy.orm import Session

from serge.models import user as user_model


def get_user(db: Session, username: str) -> user_model.User:
    return (
        db.query(user_model.User).filter(user_model.User.username == username).first()
    )


def get_user_by_email(db: Session, email: str) -> user_model.User:
    return db.query(user_model.User).filter(user_model.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[user_model.User]:
    return db.query(user_model.User).offset(skip).limit(limit).all()


def create_user(db: Session, ua: user_schema.UserAuth) -> Optional[user_model.User]:
    # Check already exists
    if get_user(db, ua.username):
        return None

    match ua.auth_type:
        case 0:
            ua.secret = get_password_hash(ua.secret)
        case _: # Todo: More auth types
            return None

    user = user_schema.User(username=ua.username)

    # Map view model onto DB models
    db_user_auth = user_model.UserAuth(
        secret=ua.secret, auth_type=ua.auth_type, user_id=user.id
    )
    db_user = user_model.User(**user.dict())
    db_user.auth.append(db_user_auth)

    db.add(db_user_auth)
    db.add(db_user)
    db.commit()
    return user


def update_user(db: Session, u: user_schema.User) -> Optional[user_model.User]:
    user = get_user(db, u.username)
    if not user:
        return None
    for k, v in u.__dict__.items():
        if k.startswith("_") or k == "auth":
            continue
        setattr(user, k, v)
    db.commit()
    return user
