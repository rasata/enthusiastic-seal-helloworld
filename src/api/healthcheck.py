from fastapi import APIRouter
from models.healthcheck import HealthcheckResponse

router = APIRouter()


@router.get("/healthcheck")
def healthcheck() -> HealthcheckResponse:
    return {
        "status": "ok",
    }
