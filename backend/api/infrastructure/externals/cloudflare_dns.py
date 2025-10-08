from cloudflare import AsyncCloudflare
from cloudflare.types.dns import RecordResponse
from fastapi_mail import MessageType
from pydantic import EmailStr
from api.common.utils import get_logger
from api.core.config import settings
from api.domain.interfaces.email_service import IEmailService
from api.interfaces.email_templates.tenant_subdomain_active_html import tenant_subdomain_active_html

logger = get_logger(__name__)

main_domain_name = settings.host_main_domain


class CloudflareDNS:
    def __init__(self, email_service: IEmailService):
        api_token = settings.cloudflare_api_token
        logger.info(f"Cloudflare API Token: {api_token}")
        self.cf = AsyncCloudflare(api_token=api_token)
        self.zone_id = settings.cloudflare_zone_id
        self.email_service = email_service
        
    async def create_cname_record(self, name: str, email_to: EmailStr):
        """Create a CNAME DNS record in Cloudflare for the given subdomain."""
        main_domain_name = settings.host_main_domain
        logger.info(f"Creating CNAME record for {name}.{main_domain_name}")
        data = {
            "type": "CNAME",
            "name": f"{name}", # e.g., company.demo.fsrapp.com
            "content": main_domain_name, # Target domain for CNAME record. Change as needed.
            "ttl": 1, # Auto TTL
            "proxied": True # Whether the record is receiving the performance and security benefits of Cloudflare.
        }
        record: RecordResponse = await self.cf.dns.records.create(zone_id=self.zone_id, **data)
        logger.info(f"Created CNAME record: {record}")
        await self.email_service.send_email(
            subject="Your subdomain is active",
            to=email_to,
            body=tenant_subdomain_active_html(subdomain_link=f"https://{name}.{main_domain_name}"),
            type=MessageType.html
        )

        return record

