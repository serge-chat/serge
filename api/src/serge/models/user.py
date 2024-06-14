from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        Uuid)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    full_name = Column(String)
    theme_light = Column(Boolean)
    default_prompt = Column(String)
    is_active = Column(Boolean, default=True)

    auth = relationship("UserAuth", back_populates="user", lazy="joined")
    chats = relationship("Chat", back_populates="user", lazy="joined")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, index=True)
    owner = Column(String, ForeignKey("users.username"))
    user = relationship("User", back_populates="chats")


class UserAuth(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True)
    secret = Column(String)
    auth_type = Column(Integer)
    user_id = Column(Uuid, ForeignKey("users.id"))

    user = relationship("User", back_populates="auth")
