from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status
from api.common.exceptions import ApiBaseException
from fastapi.responses import JSONResponse

from api.common.utils import get_host_main_domain_name, is_development_environment, get_logger

logger = get_logger(__name__)

class KnownDomainMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if is_development_environment():
            logger.warning("Development environment - skipping KnownDomainMiddleware checks")
            return await call_next(request)
        
        try:
            origin = request.headers.get('origin')
            ip = request.client.host if request.client else "unknown"

            allowed_domain = f".{get_host_main_domain_name()}"
            if origin and not origin.endswith(allowed_domain) or origin != f"https://{get_host_main_domain_name()}":
                logger.error(f"Unknown domain access attempt: {origin} from IP: {ip}")
                raise ApiBaseException(message="Unknown domain, If you are the administrator, please check your configuration. Otherwise, contact the administrator.")
            response = await call_next(request)
            return response
        except ApiBaseException as ex:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": ex.message, "code": status.HTTP_400_BAD_REQUEST}
            )

  