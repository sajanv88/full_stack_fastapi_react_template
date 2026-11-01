import asyncio

from fastapi import APIRouter, Response, status

from api.common.dtos.health_dto import HealthCheckResponseDto, ReadinessResponseDto
from api.common.utils import get_logger
from api.core.container import get_database
from api.infrastructure.externals.redis_client import redis_client

logger = get_logger(__name__)

router = APIRouter(prefix="/health")
router.tags = ["Health"]
@router.get("/", status_code=status.HTTP_200_OK, response_model=HealthCheckResponseDto)
async def health_check():
   

    return HealthCheckResponseDto(status="Ok")


async def is_reachable(check) -> bool:
    try:
        await asyncio.wait_for(check, timeout=3)
        return True
    except Exception as e:
        logger.warning(f"Readiness check failed: {e!r}")
        return False


@router.get("/ready", status_code=status.HTTP_200_OK, response_model=ReadinessResponseDto, responses={503: {"model": ReadinessResponseDto}})
async def readiness_check(response: Response):
    checks = {
        "mongodb": await is_reachable(get_database().client.admin.command("ping")),
        "redis": await is_reachable(redis_client.ping()),
    }
    is_ready = all(checks.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadinessResponseDto(status="Ok" if is_ready else "Unavailable", checks=checks)

