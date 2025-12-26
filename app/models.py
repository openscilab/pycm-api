from sqlalchemy import Boolean, Integer, Float, String
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    api_key = Column(String)
    credit = Column(Float, default=.0)
    is_active = Column(Boolean, default=True)

    cms = relationship("ConfusionMatrix", back_populates="owner")


class ConfusionMatrix(Base):
    """Confusion matrix model"""
    __tablename__ = "cms"

    id = Column(Integer, primary_key=True)
    uid = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="cms")
