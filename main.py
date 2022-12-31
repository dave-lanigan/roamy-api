import json
import pathlib
import sqlite3
import httpx
from functools import lru_cache
from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, create_engine

from schema import StreamItem
from models import CityShortData
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
    response_model = list[CityShortData]
)
def get_cities_short_data_(
    kind: str = "l",
    db: Session = Depends( get_session )
):
    return get_cities_short_data(db)


@app.get("/info/{city}/places")
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


@app.post("/posts/groups/{city}", status_code=201)
def post_group_city_post_(city: str, info: dict):
    """
    {
        "title":"",
        "content":"",
        "user":""
    }
    """
    db['posts']['group'][city].append(info)
    json_object = json.dumps(db, indent=4)
    with open("test-db.json","w+") as jf:
        jf.write(json_object)
    return info