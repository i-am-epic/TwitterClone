from email.mime import base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class Post(Base):
    __tablename__ = "posts"

    postid = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=True)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=True, server_default=text('now()'))
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    cat_name = Column(String, ForeignKey(
        "categories.cat_name", ondelete="CASCADE"), nullable=False)
    owner = relationship("User")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(String, nullable=True,unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    admin = Column(Boolean, server_default='False', nullable=False)


class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey(
        "posts.postid", ondelete="CASCADE"), primary_key=True)

class Retweet(Base):
    __tablename__ = "retweet"
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey(
        "posts.postid", ondelete="CASCADE"), primary_key=True)
    retweeted_at = Column(TIMESTAMP(timezone=True),
        nullable=False, server_default=text('now()'))


class Categories(Base):
    __tablename__ = "categories"
    cat_name = Column(String, primary_key=True, nullable=False)
    cat_id = Column(Integer)
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP(timezone=True),
        nullable=False, server_default=text('now()'))
    description = Column(String, nullable=False)

    

