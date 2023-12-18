from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from user import models
from typing import Annotated

from datab import security as security_router
from event import router as event_router
from datab.db import SessionLocal, engine
from datab.security import get_current_user
from user import router as user_router

app = FastAPI()
app.include_router(router=security_router.router)
app.include_router(router=event_router.router)
app.include_router(router=user_router.router)

models.Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]




@app.options("/api/v1/server/options", tags=["Server"])
async def get_options():
    return {}
