import logging

from fastapi import APIRouter, HTTPException

from app.app.core.celery_app import app  # Import the Celery app
from app.app.schemas.input import DateTime, Location
from app.app.schemas.output import ParkingResult
from app.app.worker.v1.tasks import predict_parking_availability

router = APIRouter()
logger = logging.getLogger(__name__)


# TODO: What about the adjacent neighborhoods? Also compute in the frontend?
@router.get(
    "/datetime/{datetime_str}/neighbourhood_id/{neighbourhood_id_str}",
    response_model=dict,
)
def read_item(
    datetime_str: str,
    neighbourhood_id_str: str,
) -> dict:
    try:
        DateTime(datetime=datetime_str)
        Location(neighbourhood_id=neighbourhood_id_str)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

    task = predict_parking_availability.delay(datetime_str, neighbourhood_id_str)
    logger.info(f"Task created: {task.id}")
    return {"task_id": task.id}


@router.get("/result/{task_id}", response_model=ParkingResult)
def get_result(task_id: str) -> ParkingResult:
    task_result = app.AsyncResult(task_id)  # Use app.AsyncResult directly
    logger.info(f"Task state: {task_result.state}")
    if task_result.state == "SUCCESS":
        result = task_result.result
        logger.info(f"Task result: {result}")
        return ParkingResult(**result)
    elif task_result.state == "PENDING":
        logger.info("Task is still pending")
        raise HTTPException(status_code=202, detail="Task is still pending")
    else:
        logger.error("Task failed")
        raise HTTPException(status_code=500, detail="Task failed")
