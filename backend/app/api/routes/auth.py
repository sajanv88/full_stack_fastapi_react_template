from fastapi import BackgroundTasks, Depends, APIRouter, Query, status, HTTPException, Response
import jwt
import logging
from jwt import InvalidTokenError

from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.core.db import get_db_reference
from app.models.user import NewUser, User, UserEmailUpdate
from app.models.role import Role
from bson import ObjectId
from typing import Annotated, Optional, Union
from fastapi.security import  OAuth2PasswordRequestForm
from app.core.token import TokenSet, verify_token, TokenData
from app.core.smtp_email import ActivationEmailSchema, send_activation_email, verify_activation_token, send_email_change_activation
from app.services.tenant_service import TenantService
from app.services.users_service import UserService
from app.core.db import  get_db_reference
from app.services.auth_service import AuthService
from app.models.tenant import Tenant
from app.core.utils import oauth2_scheme

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")
router.tags = ["Auth"]

class LoginRequest(BaseModel):
     email: str
     password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class ActivationRequest(BaseModel):
    token: str

class UserMeResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    gender: str
    role: Union[Role, None] = None
    is_active: bool = False
    activated_at: str | None = None
    image_url: str | None = None
    tenant_id: Union[str, None] = None

class ResendActivationEmailRequest(BaseModel):
    email: str
    id: str
    first_name: str

class NewRegistrationResponse(BaseModel):
    new_tenant_created: bool
    tenant: Optional[Tenant] = None



class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    new_password: str

class PasswordResetResponse(BaseModel):
    message: str


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db = Depends(get_db_reference)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        token_data = TokenData(
            email=payload["email"],
            sub=payload["sub"],
            role=payload["role"],
            is_active=payload["is_active"],
            activated_at=payload["activated_at"],
            tenant_id=payload["tenant_id"] 
        )
        logger.debug(f"Token data: {token_data}")
    except InvalidTokenError:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_user(token_data.sub)
    if user is None:
        raise credentials_exception
    return user




@router.post("/login", response_model=TokenSet)
async def login(
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()], 
     db = Depends(get_db_reference)
):
    auth_service = AuthService(db)
    try:
        return await auth_service.authenticate_user(login_request.username, login_request.password)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to authenticate: {e}"
        )


@router.post("/register", response_model=NewRegistrationResponse)
async def register(background_tasks: BackgroundTasks, new_user: NewUser, db = Depends(get_db_reference)):
    auth_service = AuthService(db)
    try:
        response = await auth_service.register_user(new_user, background_tasks)
        return NewRegistrationResponse(
            new_tenant_created=response.get("new_tenant_created", False),
            tenant=response.get("tenant", None)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to register: {e}"
        )


@router.post("/password-reset-request", response_model=PasswordResetResponse)
async def password_reset_request(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db_reference)
):
    auth_service = AuthService(db)
    try:
        await auth_service.initiate_password_reset(request.email, background_tasks)
        return PasswordResetResponse(message="If the email exists, a password reset link has been sent.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initiate password reset: {e}"
        )

@router.post("/password-reset-confirm", response_model=PasswordResetResponse)
async def password_reset_confirm(
    request: PasswordResetConfirmRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db_reference),
    token: str = Query(..., description="The password reset token"),
    user_id: str = Query(..., description="The user ID associated with the token")
):
    auth_service = AuthService(db)
    try:
        await auth_service.change_password(
            new_password=request.new_password,
            token=token,
            user_id=user_id,
            background_tasks=background_tasks
        )
        return PasswordResetResponse(message="Password has been reset successfully. A notification email has been sent!")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initiate password reset: {e}"
        )
    
@router.post("/resend_activation_email", response_class=Response)
async def resend_activation_email(
    current_user: Annotated[User, Depends(get_current_user)],
    user: ResendActivationEmailRequest,
    background_tasks: BackgroundTasks
):
    email_user = user.model_dump().copy()
    activation_email_data = ActivationEmailSchema(
        email=email_user["email"],
        user_id=str(email_user["id"]),
        first_name=email_user["first_name"],
        tenant_id=current_user.get("tenant_id", None)
    )

    background_tasks.add_task(send_activation_email, activation_email_data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserMeResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db = Depends(get_db_reference)
):
    
    print(f"Current user in /me: {current_user}")
    auth_service = AuthService(db)
    try:
        return await auth_service.me(current_user["id"])
    except Exception as e:
        print(f"Error fetching user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error happened. Please contact support."
        )


@router.post("/refresh", response_model=TokenSet)
async def refresh_token(token: RefreshRequest, db = Depends(get_db_reference)):
    auth_service = AuthService(db)
    try:
       return await auth_service.refresh_user_token(token.refresh_token)
    except InvalidTokenError:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
            )

@router.patch("/change-email", response_class=Response)
async def change_email(
    current_user: Annotated[User, Depends(get_current_user)],
    email_update: UserEmailUpdate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db_reference)
):
    user_service = UserService(db)
    user = await user_service.get_user(current_user["_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if user["email"] == email_update.new_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is the same as the current email"
        )

    result = await user_service.update_user(current_user["_id"], {
        "email": email_update.new_email,
        "is_active": False,
        "activated_at": None
    })


    if result.modified_count == 1:
        activation_email_data = ActivationEmailSchema(
                email=email_update.new_email,
                user_id=str(current_user["_id"]),
                first_name=user["first_name"],
                tenant_id=current_user.get("tenant_id", None)
            )

        background_tasks.add_task(send_email_change_activation, activation_email_data)


    return Response(status_code=status.HTTP_204_NO_CONTENT)
    

@router.post("/activate")
async def activate_account(request: ActivationRequest, db = Depends(get_db_reference)):
    """
    Activate user account using the activation token.
    """
    try:
        # Verify the activation token
        token_data = verify_activation_token(request.token)
        user_id = token_data.get("user_id")
        email = token_data.get("email"),
        tenant_id = token_data.get("tenant_id", None)
        if tenant_id:
            try:
                tenant_service = TenantService(db)
                await tenant_service.get_tenant(tenant_id)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tenant information in token"
                )

        
        # Find the user in the database
        user_service = UserService(db)
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if user is already activated
        if user.get("is_active", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is already activated"
            )
        
        # Activate the user account
        await user_service.update_user(user_id, {
            "is_active": True,
            "activated_at": datetime.utcnow()
        })

        return {
            "message": "Account activated successfully",
            "email": email
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation token has expired. Please request a new activation email."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid activation token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while activating the account"
        )
