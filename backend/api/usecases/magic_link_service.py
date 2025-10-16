from fastapi_mail import MessageType
from api.common.exceptions import ApiBaseException
from api.common.utils import get_email_sharing_link, get_host_main_domain_name
from api.domain.dtos.user_dto import UserDto
from api.domain.interfaces.email_service import IEmailService
from api.infrastructure.persistence.repositories.user_magic_link_repository_impl import UserMagicLinkRepository
from api.interfaces.email_templates.magic_link_login_template_html import magic_link_login_template
from api.usecases.tenant_service import TenantService

class EmailMagicLinkService:
    def __init__(
        self,
        user_magic_link_repo: UserMagicLinkRepository,
        email_service: IEmailService,
        tenant_service: TenantService,

    ):
        self.user_magic_link_repo: UserMagicLinkRepository = user_magic_link_repo
        self.email_service: IEmailService = email_service
        self.tenant_service: TenantService = tenant_service

    async def create_magic_link(self, user_dto: UserDto):
        """
        Create a magic link for the user and store it in the database. And valid for 5 minutes. Tries to send an email with the magic link.
        Args:
            user_id (str): The ID of the user to create the magic link for.
        """
        try:
            record = await self.user_magic_link_repo.create_magic_link(user_id=user_dto.id)
            domain = get_host_main_domain_name()
            if user_dto.tenant_id:
                tenant = await self.tenant_service.get_tenant_by_id(tenant_id=user_dto.tenant_id)
                domain = tenant.custom_domain if tenant and tenant.custom_domain else tenant.subdomain
                
            link = get_email_sharing_link(token=record.token, user_id=str(record.user_id), domain=domain, type="magic_link_login", tenant_id=str(record.tenant_id))
            html_content = magic_link_login_template(user_first_name=user_dto.first_name, magic_link=link)
            await self.email_service.send_email(
                to=user_dto.email,
                subject="Your Magic Login Link",
                type=MessageType.html,
                body=html_content
            )
        except ApiBaseException as e:
            raise e


        