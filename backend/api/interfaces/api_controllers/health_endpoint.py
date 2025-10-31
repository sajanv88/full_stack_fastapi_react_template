from fastapi import APIRouter, status

from api.common.dtos.health_dto import HealthCheckResponseDto
from api.common.utils import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/health")
router.tags = ["Health"]
@router.get("/", status_code=status.HTTP_200_OK, response_model=HealthCheckResponseDto)
async def health_check():
   

    return HealthCheckResponseDto(status="Ok")

