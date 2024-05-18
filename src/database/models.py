

from sqlalchemy import Column, Date, DateTime, Integer, String, Table, ForeignKey, func
from datetime import datetime
from sqlalchemy.orm import relationship

from db import Base



class User(Base):
    __tablename__ = "users"

    # basic details
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    created_dt = Column(DateTime, default=datetime.utcnow())

    # profile
    dob = Column(Date)
    bio = Column(String)

post_hashtags = Table(
    "post_hashtags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id")),
)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    image = Column(String)  # url to the image

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("auth.models.User", back_populates="posts")

    tags = relationship("Tag", secondary=post_hashtags, back_populates="posts")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index = True)
    name = Column(String, unique=True)

    posts = relationship("Post", secondary=post_hashtags, back_populates="tags")

    def __repr__(self):
        return self.name
    

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index = True)
    text = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())

    post_id = Column(Integer, ForeignKey("posts.id"))
    post = relationship("auth.models.Post", back_populates="comments")

    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("auth.models.User", back_populates="comments")
    