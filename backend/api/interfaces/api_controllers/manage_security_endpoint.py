from fastapi import APIRouter, Depends

from api.core.container import get_audit_logs_service, get_passkey_service
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.dtos.passkey_dto import RegisteredPasskeyCredentialsDto
from api.infrastructure.security.current_user import CurrentUser
from api.infrastructure.security.passkey_service import PasskeyService
from api.usecases.audit_logs_service import AuditLogsService


router = APIRouter(prefix="/security")
router.tags = ["Manage Security"]

@router.get("/passkeys", response_model=list[RegisteredPasskeyCredentialsDto], status_code=200)
async def get_registered_passkeys(
    current_user: CurrentUser,
    passkey_service: PasskeyService = Depends(get_passkey_service),
    audit_log_service: AuditLogsService = Depends(get_audit_logs_service)

):
    """
    Endpoint to retrieve registered passkeys for the current user.
    """
    
    passkeys = await passkey_service.get_registered_passkeys(email=current_user.email)
    res = [RegisteredPasskeyCredentialsDto(**pk.model_dump()) for pk in passkeys]
    await audit_log_service.create_audit_log(
        audit_log=AuditLogDto(
            entity="Passkey",
            action="read",
            changes={"Info": f"Retrieved {len(res)} passkeys for user {current_user.email}."},
            user_id=current_user.id,
            tenant_id=current_user.tenant_id
        )   
    )
    return res


@router.delete("/passkeys/{credential_id}", status_code=204)
async def delete_registered_passkey(
    credential_id: str,
    current_user: CurrentUser,
    passkey_service: PasskeyService = Depends(get_passkey_service),
    audit_log_service: AuditLogsService = Depends(get_audit_logs_service)
):
    """
    Endpoint to delete a registered passkey for the current user.
    """
    try:
        await passkey_service.delete_registered_passkey(
            email=current_user.email,
            credential_id=credential_id
        )
        await audit_log_service.create_audit_log(
            audit_log=AuditLogDto(
                entity="Passkey",
                action="delete",
                changes={"Info": f"Deleted passkey {credential_id} for user {current_user.email}."},
                user_id=current_user.id,
                tenant_id=current_user.tenant_id
            )   
        )
    except Exception as e:
        await audit_log_service.create_audit_log(
           audit_log=AuditLogDto(
               entity="Passkey",
               action="error",
               changes={"Info": f"Failed to delete passkey {credential_id} for user {current_user.email}."},
               user_id=current_user.id,
               tenant_id=current_user.tenant_id
           )   
        )
        raise e
    return None
