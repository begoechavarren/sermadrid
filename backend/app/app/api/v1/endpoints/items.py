import random

from fastapi import APIRouter

from app.app.schemas.output import ParkingResult

router = APIRouter()


@router.get("/datetime/{datetime}/location/{location}")
def read_item(
    datetime: str,
    location: str,  # TODO: Can use my types?
) -> ParkingResult:
    # TODO: Implement using datetime and location
    result = random.choice(["easy", "medium", "hard"])
    return ParkingResult(
        result=result,
    )
