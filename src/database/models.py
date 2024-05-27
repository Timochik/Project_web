

from sqlalchemy import (
    Column, 
    DateTime,
    Integer,
    String,
    Table,
    ForeignKey,
    func,
    Enum as SQLAEnum,
    Boolean,
    Float)
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
    posts = relationship("Post", back_populates="author")
    is_active = Column(Boolean, default=True)
    ratings = relationship("Rating", back_populates="user")
    comments = relationship("Comments", back_populates="user")


post_hashtags = Table(
    "post_hashtags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete='CASCADE')),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id")),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    image_url = Column(String)  # url to the image

    author_id = Column('author_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), default=None)
    author = relationship("User", back_populates="posts")

    hashtags = relationship("Hashtag", secondary=post_hashtags, back_populates="posts")
    qr_code_url = Column(String)
    created_dt = Column(DateTime, default=func.now())
    ratings = relationship("Rating", back_populates="image")
    comments = relationship("Comments", back_populates="image")


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    posts = relationship("Post", secondary=post_hashtags, back_populates="hashtags")


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=None, nullable=True)
    image_id = Column(ForeignKey("posts.id", ondelete='CASCADE'), nullable=False)
    user_id = Column(ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    user = relationship("User", back_populates="comments")
    image = relationship("Post", back_populates="comments")


class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    image_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    user = relationship("User", back_populates="ratings")
    image = relationship("Post", back_populates="ratings")
