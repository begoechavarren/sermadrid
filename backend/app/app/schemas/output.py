from pydantic import BaseModel


class ParkingResult(BaseModel):
    barrio: str
    result: str
    prediction: float
