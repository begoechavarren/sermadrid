from datetime import datetime

from pydantic import BaseModel
from pydantic_extra_types.coordinate import Latitude, Longitude


class Location(BaseModel):
    latitude: Latitude
    longitude: Longitude


class DateTime(BaseModel):
    datetime: datetime
