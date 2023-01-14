from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine

from schema import StreamItem
from models import CityShortData, Place
from crud import (
    get_city_streams,
    get_places_info,
    get_cities_short_data
)

#from schema import CityShortDataRM
from database import db_connect, get_session


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
    db_connect()
    

@app.get("/")
def root():
    return "Hi,there."


@app.get(
    "/cities/quick-data",
    response_model=list[CityShortData]
)
def get_cities_short_data_(
    kind: str = "l",
    db: Session = Depends( get_session )
):
    return get_cities_short_data(db)


@app.get(
    "/info/{city}/places",
    response_model=list[Place]
)
def get_city_places_info_(
    city: str,
    kind: str,
    db: Session = Depends( get_session )
):
    return get_places_info(city, kind, db)


@app.get(
    "/stream/{city}",
    #response_model=list[StreamItem]
)
def get_city_streams_(city: str, db: Session = Depends( get_session )):
    return get_city_streams(city, db)

