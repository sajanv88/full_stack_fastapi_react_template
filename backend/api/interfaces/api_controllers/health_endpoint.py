from fastapi import APIRouter, status

from api.common.dtos.health_dto import HealthCheckResponseDto


router = APIRouter(prefix="/health", tags=["Health"])
@router.get("/", status_code=status.HTTP_200_OK, response_model=HealthCheckResponseDto)
async def health_check():
    return HealthCheckResponseDto(status="Ok")

