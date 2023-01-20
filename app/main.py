"""API App and endpoints module."""

from typing import List
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from .crud import get_cities_short_data, get_city_streams, get_places_info
from .database import db_connect, get_session
from .models import CityShortData, Place

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
)


@app.on_event("startup")
def on_startup():
    """On start up."""
    db_connect()


@app.get("/")
def root():
    """Root endpoint."""
    return "Hi,there."


@app.get(
    "/cities/quick-data",
    #response_model=List[CityShortData]
)
def get_cities_short_data_(db: Session = Depends(get_session)):
    """Short data endpoint."""
    return get_cities_short_data(db)


@app.get(
    "/info/{city}/places",
    #response_model=List[Place]
)
def get_city_places_info_(city: str, kind: str, db: Session = Depends(get_session)):
    """Places info endpoint."""
    return get_places_info(city, kind, db)


@app.get(
    "/stream/{city}",
    # response_model=list[StreamItem]
)
def get_city_streams_(city: str, db: Session = Depends(get_session)):
    """City streams endpoint."""
    return get_city_streams(city, db)
