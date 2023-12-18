from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: datetime
    location: str


class CreateEventRequest(BaseModel):
    title: str
    description: str
    date: datetime
    location: str

    class Config:
        from_orm = True
        from_attributes = True


class EventModel(EventBase):
    id: int
    creator_id: int

    class Config:
        from_orm = True
        from_attributes = True