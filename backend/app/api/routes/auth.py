from fastapi import BackgroundTasks, Depends, APIRouter, status, HTTPException, Response
from jwt import InvalidTokenError
import jwt
from datetime import datetime
from pydantic import BaseModel
from app.core.db import get_db_reference
from app.models.user import NewUser, User, UserEmailUpdate
from app.models.role import Role, RoleType
from bson import ObjectId
from typing import Annotated, Optional, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.token import TokenSet, verify_refresh_token, verify_token, TokenData, generate_token_set
from app.schemas.user_schema import seralize_user_schema
from app.core.password import get_password_hash, verify_password
from app.core.smtp_email import ActivationEmailSchema, send_activation_email, verify_activation_token, send_email_change_activation
from app.core.utils import is_tenancy_enabled
from app.services.tenant_service import TenantService
from app.services.users_service import UserService
from app.core.db import client, get_db_reference
from app.core.seeder import SeedDataForNewlyCreatedTenant
from app.services.role_service import RoleService
from app.models.tenant import Tenant

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
    email: str
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", refreshUrl="api/v1/auth/refresh")


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
    except InvalidTokenError:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_user(token_data.sub)
    if user is None:
        raise credentials_exception
    return user


async def get_token_data(user, role):
 
    token_data = {
        "sub": str(user["id"]),
        "email": user["email"],
        "is_active": user["is_active"],
        "activated_at": str(user["activated_at"]) if "activated_at" in user else None,
        "tenant_id": str(user["tenant_id"]) if "tenant_id" in user else None,
        "role": role
    }
    return token_data





@router.post("/login", response_model=TokenSet)
async def login(
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()], 
     db = Depends(get_db_reference)
):
    try:
        user_service =  UserService(db)
        user = await user_service.get_raw_find_by_email(login_request.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        if not verify_password(login_request.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        role_service = RoleService(db)
        role = await role_service.get_role(user["role_id"])
        user_dump = await user_service.serialize(user)
        token_data = await get_token_data(user_dump, role)
        return generate_token_set(token_data)
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to authenticate"
        )


@router.post("/register", response_model=NewRegistrationResponse)
async def register(background_tasks: BackgroundTasks, new_user: NewUser, db = Depends(get_db_reference)):
    user_service = UserService(db)
    existing_user = await user_service.find_by_email(new_user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    role_service = RoleService(db)
    tenant_service = TenantService(db)

    hashed_password = get_password_hash(new_user.password)
    user_dict = new_user.model_dump().copy()
    user_dict["password"] = hashed_password
    user_dict["is_active"] = False  # User starts as inactive until activation
    guest_role = await role_service.find_by_name(RoleType.GUEST)
    user_dict["role_id"] = ObjectId(guest_role["id"])
    user_dict["created_at"] = datetime.utcnow()
    tenant_id = None
    
    if is_tenancy_enabled():
        sub_domain = user_dict['sub_domain']
        if sub_domain is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subdomain is required"
            )
        
        try:
            result = await tenant_service.create_tenant({
                "name": sub_domain.split(".")[0],
                "sub_domain": sub_domain
            })
            if result.inserted_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create tenant"
                )
            tenant_id = str(result.inserted_id)
            print("Tenant created:", result.inserted_id)
            user_dict["tenant_id"] = ObjectId(result.inserted_id)
            db = client[f"tenant_{tenant_id}"]
            user_service = UserService(db)
            tenant_seeder = SeedDataForNewlyCreatedTenant(db)
            background_tasks.add_task(tenant_seeder.fill_roles, user_dict["email"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

 
    
    result = await user_service.create_user(user_dict)

    if result.inserted_id:
        activation_email_data = ActivationEmailSchema(
                email=user_dict["email"],
                user_id=str(result.inserted_id),
                first_name=user_dict["first_name"],
                tenant_id=str(user_dict["tenant_id"]) if user_dict["tenant_id"] in user_dict else None
            )
        background_tasks.add_task(send_activation_email, activation_email_data)
    else:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
        )

    if tenant_id is not None:
        tenant = await tenant_service.get_tenant(tenant_id)
        return NewRegistrationResponse(
            tenant=tenant,
            new_tenant_created=True
        )
    else:
        return NewRegistrationResponse(
            tenant=None,
            new_tenant_created=False
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
        first_name=email_user["first_name"]
    )

    background_tasks.add_task(send_activation_email, activation_email_data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserMeResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db = Depends(get_db_reference)
):
    
    print(f"Current user in /me: {current_user}")
    try:
        user_service = UserService(db)
        role_service = RoleService(db)
        user = await user_service.get_user(current_user["id"])
        user["role"] = await role_service.get_role(user["role_id"])
        return user
    except Exception as e:
        print(f"Error fetching user details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error happened. Please contact support."
        )


@router.post("/refresh", response_model=TokenSet)
async def refresh_token(token: RefreshRequest, db = Depends(get_db_reference)):
    try:
        refresh_token = token.refresh_token
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        user_service = UserService(db)
        user = await user_service.get_user(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        role_service = RoleService(db)
        role = await role_service.get_role(user["role_id"])
        token_data = await get_token_data(user, role)
        return generate_token_set(token_data)
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
                first_name=user["first_name"]
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
        email = token_data.get("email")
        
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
