from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from datab.db import Base
from event.models import event_user


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

    events = relationship("Event", back_populates="creator")
    events_attending = relationship("Event", secondary=event_user, back_populates="attendees")
