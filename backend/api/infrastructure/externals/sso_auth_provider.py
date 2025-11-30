from typing import Dict
from fastapi import Request
from api.common.exceptions import InvalidOperationException
from api.common.utils import get_host_main_domain_name, get_logger
from api.domain.entities.sso_settings import SSOProvider, SSOSettings
import fastapi_sso
from api.core.config import settings

from api.usecases.sso_settings_service import SSOSettingsService
from api.usecases.tenant_service import TenantService

logger = get_logger(__name__)

class SSOAuthProvider:
    def __init__(self, sso_settings_service: SSOSettingsService, tenant_service: TenantService):
        self.sso_settings_service: SSOSettingsService = sso_settings_service
        self.tenant_service: TenantService = tenant_service
        self.redirect_uri_to_app = None
    
    async def _provider_instance(self, provider_name: SSOProvider, sso_provider: SSOSettings) -> fastapi_sso.SSOBase:
        domain = None
        http_protocol = "https" if settings.fastapi_env == "production" else "http"
        if sso_provider.tenant_id:
            tenant = await self.tenant_service.get_tenant_by_id(tenant_id=sso_provider.tenant_id)
            domain = f"{http_protocol}://{tenant.custom_domain}" if tenant.custom_domain else f"{http_protocol}://{tenant.subdomain}"
        else:
            domain = f"{http_protocol}://{get_host_main_domain_name()}"

        allow_insecure_http = settings.fastapi_env != "production"
        redirect_uri = f"{domain}/api/v1/account/sso/{provider_name}/callback"
        self.redirect_uri_to_app = domain

        sso: fastapi_sso.SSOBase = None
        match provider_name:
            case "google":
                sso = fastapi_sso.GoogleSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case "github":
                sso = fastapi_sso.GithubSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case "discord":
                sso = fastapi_sso.DiscordSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case "microsoft":
                sso = fastapi_sso.MicrosoftSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case "linkedin":
                sso = fastapi_sso.LinkedInSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case "notion":
                sso = fastapi_sso.NotionSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case "gitlab":
                sso = fastapi_sso.GitlabSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case "bitbucket":
                sso = fastapi_sso.BitbucketSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case "x", "twitter":
                sso = fastapi_sso.TwitterSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    allow_insecure_http=allow_insecure_http,
                    redirect_uri=redirect_uri,
                    scope=sso_provider.scopes
                )
            case "facebook":
                sso = fastapi_sso.FacebookSSO(
                    client_id=sso_provider.client_id,
                    client_secret=sso_provider.client_secret,
                    redirect_uri=redirect_uri,
                    allow_insecure_http=allow_insecure_http,
                    scope=sso_provider.scopes
                )
            case _:
                raise InvalidOperationException(f"SSO provider '{provider_name}' is not supported.")
            
        return sso


    async def _get_sso_settings(self, provider_name: SSOProvider) -> SSOSettings:
        sso_provider = await self.sso_settings_service.get_provider(provider_name)
        if not sso_provider.enabled:
            logger.error(f"SSO provider '{provider_name}' is not enabled.")
            raise InvalidOperationException(f"SSO provider '{provider_name}' is not enabled.")
        return sso_provider


    async def login(self, provider_name: SSOProvider):
        sso_provider = await self._get_sso_settings(provider_name)
        logger.info(f"Initiating login for SSO provider: {provider_name}")
        sso = await self._provider_instance(provider_name, sso_provider)
        redirect = await sso.get_login_redirect()
        logger.info(f"Redirecting to SSO provider: {provider_name} for authentication")
        return redirect
    

    async def callback(self, provider_name: SSOProvider, req: Request) -> fastapi_sso.OpenID:
        sso_provider = await self._get_sso_settings(provider_name)
        sso = await self._provider_instance(provider_name, sso_provider)
        user = await sso.verify_and_process(req)
        logger.info(f"SSO callback processed for provider: {provider_name}")
        return user
    
    def get_redirect_uri_to_app(self) -> str:
        if not self.redirect_uri_to_app:
            raise InvalidOperationException("Redirect URI to app is not set.")
        return self.redirect_uri_to_app