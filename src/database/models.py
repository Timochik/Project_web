

from sqlalchemy import Column, Date, DateTime, Integer, String, Table, ForeignKey, func, Enum as SQLAEnum, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

Base = declarative_base()
class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    moderator = "moderator"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SQLAEnum(UserRole), default=UserRole.user)


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=None, nullable=True)
    image_id = Column(ForeignKey("posts.id", ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)




# class Tag(Base):
#     __tablename__ = "tags"
#     id = Column(Integer, primary_key=True, index = True)
#     name = Column(String, unique=True)

#     posts = relationship("Post", secondary=post_hashtags, back_populates="tags")

#     def __repr__(self):
#         return self.name
    

# class Comment(Base):
#     __tablename__ = "comments"
#     id = Column(Integer, primary_key=True, index = True)
#     text = Column(String)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now())

#     post_id = Column(Integer, ForeignKey("posts.id"))
#     post = relationship("auth.models.Post", back_populates="comments")

#     author_id = Column(Integer, ForeignKey("users.id"))
#     author = relationship("auth.models.User", back_populates="comments")
    