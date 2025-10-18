from fastapi import APIRouter, Depends

from api.core.container import get_passkey_service
from api.domain.dtos.passkey_dto import RegisteredPasskeyCredentialsDto
from api.infrastructure.security.current_user import CurrentUser
from api.infrastructure.security.passkey_service import PasskeyService


router = APIRouter(prefix="/security")
router.tags = ["Manage Security"]

@router.get("/passkeys", response_model=list[RegisteredPasskeyCredentialsDto], status_code=200)
async def get_registered_passkeys(
    current_user: CurrentUser,
    passkey_service: PasskeyService = Depends(get_passkey_service)
):
    """
    Endpoint to retrieve registered passkeys for the current user.
    """
    
    passkeys = await passkey_service.get_registered_passkeys(email=current_user.email)
    return [RegisteredPasskeyCredentialsDto(**pk.model_dump()) for pk in passkeys]


@router.delete("/passkeys/{credential_id}", status_code=204)
async def delete_registered_passkey(
    credential_id: str,
    current_user: CurrentUser,
    passkey_service: PasskeyService = Depends(get_passkey_service)
):
    """
    Endpoint to delete a registered passkey for the current user.
    """
    await passkey_service.delete_registered_passkey(
        email=current_user.email,
        credential_id=credential_id
    )
    return None
