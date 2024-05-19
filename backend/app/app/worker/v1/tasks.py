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
    # from sermadrid.pipelines import SerMadridInferencePipeline
    # import pandas as pd

    # sermadrid_inference = SerMadridInferencePipeline(
    #     artifacts_path="artifacts",
    #     spaces_path="data/spaces",
    # )

    # # Example datetime for single prediction
    # DATETIME_SINGLE = pd.to_datetime("2024-08-16 11:00:00")
    # BARRIO_ID = "405"

    # predictions = sermadrid_inference.run(
    #     datetime=DATETIME_SINGLE,
    #     barrio_id=BARRIO_ID,
    #     return_percentage=True,
    # )
    result = random.choice(["easy", "medium", "hard"])
    return {"result": result}
