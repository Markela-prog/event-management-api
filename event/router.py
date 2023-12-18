from fastapi import status
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from datab.db import SessionLocal
from datab.security import get_current_user
from event.models import Event
from event.schemas import CreateEventRequest, EventModel
from user.models import Users

router = APIRouter(
    prefix='/event',
    tags=['event']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_event(event: CreateEventRequest, db: db_dependency, current_user: user_dependency):
    if current_user["role"] != "creator":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    create_event_model = Event(
        title=event.title,
        description=event.description,
        date=event.date,
        location=event.location,
        creator_id=current_user["id"],
    )
    db.add(create_event_model)
    db.commit()
    return EventModel.from_orm(create_event_model)

@router.get("/", response_model=List[EventModel])
def get_all_events(db: db_dependency, skip: int=0, limit: int=100):
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@router.get("/{id}", response_model=EventModel)
def get_event_by_id(id: int, db: db_dependency, current_user: user_dependency):
    event = db.query(Event).filter(Event.id == id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{id}", response_model=EventModel)
def update_event(id: int, event: CreateEventRequest, db: db_dependency,
                 current_user: user_dependency):
    db_event = db.query(Event).filter(Event.id == id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if db_event.creator_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    for key, value in event.dict().items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.delete("/{id}")
def delete_event(id: int, db: db_dependency, current_user: user_dependency):
    db_event = db.query(Event).filter(Event.id == id).first()
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if db_event.creator_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(db_event)
    db.commit()
    return {"detail": "Event deleted"}

@router.post("/join-event/{id}")
def join_event(id: int, db: db_dependency, current_user: user_dependency):
    event = db.query(Event).filter(Event.id == id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    user = db.query(Users).filter(Users.id == current_user["id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user in event.attendees:
        raise HTTPException(status_code=400, detail="User has already joined the event")
    event.attendees.append(user)
    db.commit()
    return {"detail": "Successfully joined the event"}


@router.delete("/leave-event/{id}")
def leave_event(id: int, db: db_dependency, current_user: user_dependency):
    event = db.query(Event).filter(Event.id == id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    user = db.query(Users).filter(Users.id == current_user["id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user not in event.attendees:
        raise HTTPException(status_code=400, detail="User has not joined the event")
    event.attendees.remove(user)
    db.commit()
    return {"detail": "Successfully left the event"}

@router.get("/user/joined-events")
def get_joined_events(db: db_dependency, current_user: user_dependency):
    user = db.query(Users).filter(Users.id == current_user["id"]).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        joined_events = [event.id for event in user.events_attending]
        return joined_events
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))



@router.get("/events/{id}/attendees", response_model=int)
def get_attendee_count(id: int, db: db_dependency):
    event = db.query(Event).filter(Event.id == id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return len(event.attendees)