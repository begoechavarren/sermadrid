from pydantic import BaseModel


class ParkingResult(BaseModel):
    barrio: str
    prediction: float
