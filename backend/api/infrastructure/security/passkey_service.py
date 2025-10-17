from typing import List
from beanie import PydanticObjectId
from fastapi import Body
from pydantic import EmailStr
from webauthn import (
    generate_registration_options,
    generate_authentication_options,
    options_to_json,
    verify_registration_response,
    verify_authentication_response,
)

from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    AuthenticatorTransport,
    PublicKeyCredentialType,
    UserVerificationRequirement,
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)


import base64

from api.common.dtos.passkey_rep_dto import PasskeyRepDto
from api.common.utils import get_logger, get_host_main_domain_name, get_app_title, get_utc_now
from api.core.exceptions import PassKeyException
from api.domain.dtos.user_dto import UserDto
from api.domain.entities.user_passkey import Credential, UserPasskey
from api.infrastructure.persistence.repositories.user_passkey_repository_impl import UserPasskeyChallengesRepository, UserPasskeyRepository

logger = get_logger(__name__)

def decode_base64url(data: str) -> bytes:
    data += '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data)

class PasskeyService():
    def __init__(
            self, 
            user_passkey_repo: UserPasskeyRepository = UserPasskeyRepository,
            challenges_repo: UserPasskeyChallengesRepository = UserPasskeyChallengesRepository
        ):
        logger.info("PasskeyService initialized.")
        self.user_passkey_repo: UserPasskeyRepository = user_passkey_repo
        self.challenges_repo: UserPasskeyChallengesRepository = challenges_repo


    async def _get_rep_id_and_name(self, tenant_id: PydanticObjectId | None = None) -> PasskeyRepDto:
        """
          Helper method to get the relying party ID and name based on tenant information.
        """
        if tenant_id is None:
            return PasskeyRepDto(
                rp_id=get_host_main_domain_name(),
                rp_name=get_app_title()
            )
        
        from api.usecases.tenant_service import TenantService
        from api.core.container import get_tenant_service
        tenant_service: TenantService = get_tenant_service()

        if tenant_id is not None:
            tenant = await tenant_service.get_tenant_by_id(tenant_id=str(tenant_id))
            rp_id = tenant.custom_domain if tenant.custom_domain else tenant.subdomain
            rp_name = tenant.name.title()
            return PasskeyRepDto(rp_id=rp_id, rp_name=rp_name)


    async def register_options(self, user_dto: UserDto) -> str:
        """
        Generate registration options for a user. If the user does not have a passkey record, create one. Add a challenge to the challenges collection with an expiration time.
        """
        user = await self.user_passkey_repo.single_or_none(user_email=user_dto.email)
        if not user:
            user_passkey = UserPasskey(user_email=user_dto.email, credentials=[], tenant_id=user_dto.tenant_id)
            await self.user_passkey_repo.create(user_passkey.model_dump())

        
        rep = await self._get_rep_id_and_name(tenant_id=user_dto.tenant_id)
        registration_options = generate_registration_options(
            rp_name=rep.rp_name,
            rp_id=rep.rp_id,
            user_id=str(user_dto.email).encode(),
            user_name=user_dto.email,
            user_display_name=user_dto.first_name + " " + user_dto.last_name,
            attestation=AttestationConveyancePreference.NONE,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=UserVerificationRequirement.REQUIRED
            )
        )

        await self.challenges_repo.save_challenge(
            email=user_dto.email,
            challenge=registration_options.challenge,
            type="registration",
            tenant_id=user_dto.tenant_id if user_dto.tenant_id else None
        )

        return options_to_json(registration_options)

    async def complete_registration(self, email: EmailStr, credential: dict = Body(...)) -> bool:
        """
        Complete the registration process by verifying the registration response. 
        If successful, store the new credential in the user's passkey record and remove the used challenge.
        Raises PassKeyException on failure.
        """
        expected_challenge = await self.challenges_repo.get_challenge(email=email, type="registration")
        if expected_challenge is None:
            raise PassKeyException("No expected challenge found or challenge expired.")

        rep = await self._get_rep_id_and_name(expected_challenge.tenant_id)


        verified = verify_registration_response(
            credential=credential,
            expected_challenge=decode_base64url(expected_challenge.challenge),
            expected_rp_id=rep.rp_id,
            expected_origin=f"https://{rep.rp_id}",
            require_user_verification=False,
        )

        user_passkey = await self.user_passkey_repo.single_or_none(user_email=email)
        if user_passkey is None:
            raise PassKeyException("User passkey record not found.")
        

        cred_data = Credential(
            credential_id=base64.urlsafe_b64encode(verified.credential_id).decode(),
            public_key=base64.urlsafe_b64encode(verified.credential_public_key).decode(),
            sigin_count=verified.sign_count,
            transports=[AuthenticatorTransport.INTERNAL, AuthenticatorTransport.HYBRID],
            created_at=get_utc_now().isoformat(),
        )
        user_passkey.credentials.append(cred_data)
        user_passkey.credentials = user_passkey.credentials.copy()
        await user_passkey.save()
        await self.challenges_repo.delete_challenge(email=email, type="registration")
        return True
    


    async def auth_login_options(self, user_dto: UserDto) -> str:
        """
        Generate authentication options for a user. Raises PassKeyException if no credentials are found.
        """
        user = await self.user_passkey_repo.single_or_none(user_email=user_dto.email)
        if not user or len(user.credentials) == 0:
            raise PassKeyException("No credentials found for the user. Please register first.")
        
        user_credentials = user.credentials
        allow_credentials: List[PublicKeyCredentialDescriptor] = [
                PublicKeyCredentialDescriptor(
                    type=PublicKeyCredentialType.PUBLIC_KEY,
                    id=base64.urlsafe_b64decode(cred.credential_id),
                    transports=cred.transports)
                for cred in user_credentials
            ]

        rep = await self._get_rep_id_and_name(tenant_id=user.tenant_id)
        login_options = generate_authentication_options(
            rp_id=rep.rp_id,
            user_verification=UserVerificationRequirement.REQUIRED,
            allow_credentials=allow_credentials
        )

        await self.challenges_repo.save_challenge(
            email=user_dto.email,
            challenge=login_options.challenge,
            type="authentication",
            tenant_id=user_dto.tenant_id if user_dto.tenant_id else None
        )

        return options_to_json(login_options)


    async def complete_auth_login(self, email: EmailStr, credential: dict = Body(...)) -> bool:
        """
        Complete the authentication process by verifying the authentication response. 
        If successful, update the sign-in count for the credential and remove the used challenge.
        Raises PassKeyException on failure.
        """
        expected_challenge = await self.challenges_repo.get_challenge(email=email, type="authentication")
        if expected_challenge is None:
            raise PassKeyException("No expected challenge found or challenge expired.")

        user_passkey = await self.user_passkey_repo.single_or_none(user_email=email)

        if user_passkey is None or len(user_passkey.credentials) == 0:
            raise PassKeyException("No credentials found for the user. Please register first.")
        
        rep = await self._get_rep_id_and_name(expected_challenge.tenant_id)

        user_credentials = user_passkey.credentials

        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=decode_base64url(expected_challenge.challenge),
            expected_rp_id=rep.rp_id,
            expected_origin=f"https://{rep.rp_id}",
            credential_public_key=[
                base64.urlsafe_b64decode(cred.public_key) for cred in user_credentials
            ][0],
            credential_current_sign_count=[
                cred.sigin_count for cred in user_credentials
            ][0],
            require_user_verification=True,
        )

        # Update sign-in count
        for cred in user_credentials:
            if  cred.credential_id == base64.urlsafe_b64encode(verified.credential_id).decode():
                cred.sigin_count = verified.new_sign_count
                break
        
        await user_passkey.save()
        await self.challenges_repo.delete_challenge(email=email, type="authentication")
        logger.info(f"Passkey Authentication verified for user {email}.")
        return True
    

    async def has_passkeys(self, email: EmailStr) -> bool:
        """
        Check if a user has any registered passkeys.
        """
        user = await self.user_passkey_repo.single_or_none(user_email=email)
        return user is not None and len(user.credentials) > 0