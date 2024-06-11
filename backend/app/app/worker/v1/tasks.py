import random

from app.app.core.celery_app import app, models, spaces_dict
from app.app.schemas.output import ParkingResult
from sermadrid.pipelines import SerMadridInferencePipeline


@app.task
def predict_parking_availability(
    datetime_str: str, neighbourhood_id_str: str
) -> ParkingResult:
    SERMADRID_INFERENCE = SerMadridInferencePipeline()
    MODEL = models.get(neighbourhood_id_str)

    prediction = SERMADRID_INFERENCE.run(
        datetime=datetime_str,
        model=MODEL,
        num_plazas=spaces_dict[neighbourhood_id_str]["num_plazas"],
        return_percentage=True,
    )[0]
    result = random.choice(["easy", "medium", "hard"])
    return {
        "barrio": spaces_dict[neighbourhood_id_str]["barrio"],
        "result": result,
        "prediction": prediction,
    }
