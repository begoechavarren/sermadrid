from pydantic import BaseModel


class ParkingResult(BaseModel):
    result: str
    prediction: float
