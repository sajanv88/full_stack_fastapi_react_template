from pydantic import EmailStr
from api.common.utils import get_logger, get_host_main_domain_name
from api.domain.interfaces.background_task import IBackgroundTask
from api.infrastructure.externals.cloudflare_dns import CloudflareDNS


logger = get_logger(__name__)

class AddDnsRecordTaskService(IBackgroundTask):
    def __init__(self, cloudflare_service: CloudflareDNS):
        self.cloudflare_service = cloudflare_service
        logger.info("Initialized AddDnsRecordTaskService.")

    async def _init_and_run(self, subdomain: str, email_to: EmailStr) -> None:
        try:
            await self.cloudflare_service.create_cname_record(name=subdomain, email_to=email_to)
            logger.info(f"Successfully added DNS record for subdomain: {subdomain}")
            logger.info("Notification email sent.")
        except Exception as ex:
            logger.error(f"Failed to add DNS record for subdomain {subdomain}: {ex}")
            raise ex

    async def enqueue(self, subdomain: str, email_to: EmailStr) -> None:
        logger.info(f"Enqueuing dns record addition task for subdomain: {subdomain}.{get_host_main_domain_name()}")
        return await self._init_and_run(subdomain=subdomain, email_to=email_to)
    