from beanie import PydanticObjectId
from fastapi_mail import MessageType
from api.common.exceptions import ApiBaseException
from api.common.utils import get_email_sharing_link, get_host_main_domain_name
from api.domain.dtos.user_dto import UserDto
from api.domain.interfaces.email_service import IEmailService
from api.infrastructure.persistence.repositories.user_magic_link_repository_impl import UserMagicLinkRepository
from api.interfaces.email_templates.magic_link_login_template_html import magic_link_login_template
from api.usecases.tenant_service import TenantService
from api.common.security import hash_it, JWT_SECRET, validate_hashed_value


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
            user_dto (UserDto): The user data transfer object containing user information.
        """
        try:
            token = hash_it(user_dto.id + JWT_SECRET)
            record = await self.user_magic_link_repo.create_magic_link(user_id=user_dto.id, token=token)
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


    async def validate_magic_link(self, user_id: str, token: str) -> bool:
        """
        Validate the magic link token for the given user ID.
        Args:
            user_id (str): The ID of the user to validate the magic link for.
            token (str): The token to validate.
        Returns:
            bool: True if the token is valid, False otherwise.
        """
        await self.user_magic_link_repo.clear_cache()
        record = await self.user_magic_link_repo.single_or_none(user_id=PydanticObjectId(user_id), token=token)
        print("Record:", record)
        if record is None:
            return False
        
        result = validate_hashed_value(value=user_id, hashed_value=token)
        if result:
            # Optionally, you can delete the magic link after successful validation to prevent reuse
            await self.user_magic_link_repo.clear_cache()
            await self.user_magic_link_repo.delete(id=str(record.id))

        await self.user_magic_link_repo.clear_cache()
        return result
        
