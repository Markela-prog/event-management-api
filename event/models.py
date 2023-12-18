from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datab.db import Base


# Association table
event_user = Table(
    'event_user', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    date = Column(DateTime)
    location = Column(String)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator = relationship("Users", back_populates="events")
    attendees = relationship("Users", secondary=event_user, back_populates="events_attending")
