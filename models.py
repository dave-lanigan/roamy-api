import uuid
from typing import Optional
from sqlmodel import Field, SQLModel


class Place(SQLModel, table=False):

    __tablename__ = "places"

    name: str
    address: str
    blurb: Optional[str]
    city_tag: str
    lat: float
    lon: float
    img: str


class StreamItem(SQLModel, table=False):
    
    title: str
    content: Optional[str] = None
    post_id: Optional[str] = str( uuid.uuid4() )
    source: str
    link: str
    img: Optional[str] = None


class CityShortData(SQLModel, table=True):
    
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