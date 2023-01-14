"""
Database models for tables.
"""
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel


class Place(SQLModel, table=True):
    """A table for places."""

    __tablename__ = "places"

    pid: Optional[int] = Field(primary_key=True)
    kind: str
    name: str
    address: str
    blurb: Optional[str]
    link: Optional[str]
    lat: float
    lon: float
    img: str
    rating: float
    city_tag: str


class StreamItem(SQLModel):
    """A table object for stream items from reddit and twitter."""

    title: str
    content: Optional[str] = None
    post_id: Optional[str] = str(uuid.uuid4())
    source: str
    link: str
    img: Optional[str] = None


class CityShortData(SQLModel, table=True):
    """A table for city short data."""

    __tablename__ = "city_short_data"

    tag: Optional[str] = Field(primary_key=True)
    name: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    iso3: Optional[str]
    country: Optional[str]
    airbnb: Optional[str]
    food: Optional[int]
    rides: Optional[str]
    internet: Optional[str]
    english: Optional[str]
    safety: Optional[str]
    avg_cost: Optional[int]
    img: Optional[str]
    complete: bool = False
