from datetime import datetime

from pydantic import BaseModel


# TODO: Use in endpoints
# TODO: Change name to Location
class Location(BaseModel):
    # TODO: Change to int?
    neighbourhood_id: str


class DateTime(BaseModel):
    datetime: datetime
