import dns.resolver

from api.common.utils import get_logger
from api.core.exceptions import InvalidCustomDomainException
from api.domain.dtos.user_dto import UserDto
from api.domain.interfaces.email_service import IEmailService
from api.interfaces.email_templates.dns_notification_html import dns_notification_email
logger = get_logger(__name__)
class DnsResolver:
    def __init__(self, email_service: IEmailService):
        self.email_service = email_service
    
    async def resolve(self, hostname: str, expected_target: str) -> bool:
        """
        Resolve the given domain to its DNS records.
        - Must resolve via DNS
        - DNS result must include `expected_target` (CNAME or A record)
        """
        try:
            answers = dns.resolver.resolve(hostname, 'CNAME')
            cname_targets = [rdata.target.to_text().rstrip('.') for rdata in answers]
            resolved_to = cname_targets
            record_type = "CNAME"
        except dns.resolver.NoAnswer:
            try:
                answers = dns.resolver.resolve(hostname, 'A')
                resolved_to = [rdata.address for rdata in answers]
                record_type = "A"
            except Exception as e:
                raise InvalidCustomDomainException(f"DNS resolution failed for {hostname}: {e}")
        except Exception as e:
            raise InvalidCustomDomainException(f"DNS resolution failed for {hostname}: {e}")

        if expected_target:
            if not any(expected_target in target for target in resolved_to):
                raise InvalidCustomDomainException(
                    f"DNS {record_type} record for {hostname} does not point to the expected target ({expected_target}). Found: {resolved_to}"
                )

        return True
    
    async def notify_dns_status(self, user_info: UserDto,  hostname: str, is_success: bool, message: str):
        logger.info(f"Sending DNS status notification to {user_info.email} for hostname {hostname} with status {'Success' if is_success else 'Failed'}")
        await self.email_service.send_email(
            subject="DNS Configuration Status",
            to=user_info.email,
            body=dns_notification_email(
                user_first_name=user_info.first_name,
                hostname=hostname,
                status="Success" if is_success else "Failed"
            ),
            type="html"
        )