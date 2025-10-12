## Note: This is just for Coolify integration. You must have a Coolify instance running with API access enabled.
## Documentation: https://coolify.io/docs

import httpx

from api.common.utils import get_logger
from api.core.exceptions import CoolifyIntegrationException
from api.domain.dtos.coolify_app_dto import CoolifyAppDto, UpdateDomainDto
from api.core.config import settings
logger = get_logger(__name__)

class CoolifyApp:
    """Coolify application integration."""

    def __init__(self):
        self.api_url = settings.coolify_api_url
        self.api_key = settings.coolify_api_key
        self.application_id = settings.coolify_application_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def get_app_details(self) -> CoolifyAppDto:
        """
            Fetch the Coolify application details.
            Raises CoolifyIntegrationException if fetching app details fails.
            Returns CoolifyAppDto on success.
        """
        if settings.coolify_enabled is False:
            raise CoolifyIntegrationException("Coolify integration is not enabled in settings.")
        
        url = f"{self.api_url}/applications/{self.application_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"Failed to fetch Coolify app details: {response.text}")
                raise CoolifyIntegrationException(f"{response.text}")
            
            data: CoolifyAppDto = response.json()
            return CoolifyAppDto(**data)
            
    async def update_domain(self, data: UpdateDomainDto) -> bool:
        """
            Update the Coolify application with the new domain.
            also, raises CoolifyIntegrationException if fetching app details fails.
            Returns True if successful, False otherwise.

            @param data: UpdateDomainDto containing domain and mode ('add' or 'remove')
            mode: 'add' to add a domain, 'remove' to remove a domain
            domain: the domain to add or remove
        """
        if settings.coolify_enabled is False:
            raise CoolifyIntegrationException("Coolify integration is not enabled in settings.")
        
        try:
            app_data = await self.get_app_details()
            domains = [d.strip() for d in app_data.fqdn.split(",") if d.strip()]
            if data.mode == "add":
                if data.domain not in domains:
                    domains.append(data.domain)
            elif data.mode == "remove":
                if data.domain in domains:
                    domains.remove(data.domain)
            
            new_domains = ",".join(domains)
            logger.debug(f"Updating Coolify app domains to: {new_domains}")

            url = f"{self.api_url}/applications/{self.application_id}"
            payload = {
                "domains": new_domains
            }
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, json=payload, headers=self.headers)
                if response.status_code == 200:
                    return True
                
                logger.error(f"Failed to update Coolify app: {response.text}")
                return False
        except CoolifyIntegrationException as e:
            logger.error(f"Error fetching app details: {e}")
            raise e

    async def restart_app(self) -> bool:
        """
            Restart the Coolify application.
            Raises CoolifyIntegrationException if restarting the app fails.
            Returns True if successful, False otherwise.
        """
        if settings.coolify_enabled is False:
            raise CoolifyIntegrationException("Coolify integration is not enabled in settings.")
        
        url = f"{self.api_url}/applications/{self.application_id}/restart"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers)
            if response.status_code == 200:
                return True
            
            logger.error(f"Failed to restart Coolify app: {response.text}")
            raise CoolifyIntegrationException(f"{response.text}")
