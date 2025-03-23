from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from infrastructure.models.alchemy.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True)
    first_name = Column(String, index=True, nullable=True)
    last_name = Column(String, index=True, nullable=True)
    middle_name = Column(String, index=True, nullable=True)
    registration_date = Column(DateTime, default=datetime.now)
    is_banned = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    photo = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    routes = relationship("Route", back_populates="author")
    likes = relationship("Like", back_populates="author")
    comments = relationship("RouteComment", back_populates="author")

