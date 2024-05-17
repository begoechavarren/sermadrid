import random

from app.app.core.celery_app import app
from app.app.schemas.input import DateTime, Location
from app.app.schemas.output import ParkingResult


@app.task
def predict_parking_availability(
    datetime_str: str, latitude_str: str, longitude_str: str
) -> ParkingResult:
    datetime = DateTime(datetime=datetime_str)
    location = Location(latitude=latitude_str, longitude=longitude_str)
    print(f"Predicting parking availability for {datetime} at {location}")
    # TODO: Implement real logic
    result = random.choice(["easy", "medium", "hard"])
    return {"result": result}
