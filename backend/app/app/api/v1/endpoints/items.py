import logging

from fastapi import APIRouter, Depends, HTTPException

from app.app.core.dependencies import get_models_and_spaces
from app.app.core.prediction import predict_parking_availability
from app.app.schemas.input import DateTime, Location
from app.app.schemas.output import ParkingResult

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/datetime/{datetime_str}/neighbourhood_id/{neighbourhood_id_str}",
    response_model=ParkingResult,
)
def read_item(
    datetime_str: str,
    neighbourhood_id_str: str,
    models_and_spaces: tuple = Depends(get_models_and_spaces),
) -> ParkingResult:
    try:
        DateTime(datetime=datetime_str)
        Location(neighbourhood_id=neighbourhood_id_str)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

    models, spaces_dict = models_and_spaces
    result = predict_parking_availability(
        datetime_str, neighbourhood_id_str, models, spaces_dict
    )
    logger.info(f"Prediction result: {result}")
    return ParkingResult(**result)
