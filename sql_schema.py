from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import backref, declarative_base, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.types import JSON

Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"
    title = Column(String(128))
    url = Column(String(1024))
