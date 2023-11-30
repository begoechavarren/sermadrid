import random

from fastapi import APIRouter, HTTPException

from app.app.schemas.input import DateTime, Location
from app.app.schemas.output import ParkingResult

router = APIRouter()


@router.get(
    "/datetime/{datetime_str}/latitude/{latitude_str}/longitude/{longitude_str}"
)
def read_item(
    datetime_str: str,
    latitude_str: str,
    longitude_str: str,
) -> ParkingResult:
    try:
        datetime = DateTime(datetime=datetime_str)
        location = Location(latitude=latitude_str, longitude=longitude_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # TODO: Call package
    print(datetime)
    print(location)
    result = random.choice(["easy", "medium", "hard"])
    return ParkingResult(
        result=result,
    )
