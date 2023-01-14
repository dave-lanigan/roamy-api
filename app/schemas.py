import uuid
from typing import Optional

from pydantic import BaseModel


class StreamItem(BaseModel):
    title: str
    content: Optional[str] = None
    post_id: str = str(uuid.uuid4())
    source: str
    link: str
    img: Optional[str] = None


class CityShortDataRM(BaseModel):
    tag: str
    name: str
    lat: float
    lon: float
    iso3: Optional[str] = None
    iata: Optional[str] = None
    country: Optional[str] = None
    airbnb: Optional[str] = None
    food: Optional[int] = None
    rides: Optional[str] = None  # uber
    internet: Optional[str] = None  #
    english: Optional[str] = None  # pdf
    safety: Optional[str] = None  # numbeo
    avg_cost: Optional[int] = None  # groceries + flight + airbnb
    complete: bool = False
