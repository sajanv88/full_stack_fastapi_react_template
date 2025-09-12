import logging
from datetime import datetime
from bson import ObjectId
from fastapi import BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from streamlit import status
from app.services.users_service import UserService
from app.core.password import get_password_hash, verify_password
from app.services.role_service import RoleService
from app.core.token import TokenSet, verify_refresh_token, generate_token_set
from app.services.tenant_service import TenantService
from app.models.user import NewUser
from app.models.role import RoleType
from app.core.utils import is_tenancy_enabled
from app.core.db import client
from app.core.seeder import SeedDataForNewlyCreatedTenant
from app.core.smtp_email import ActivationEmailSchema, send_activation_email


logger = logging.getLogger(__name__)

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

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def authenticate_user(self, email: str, password: str):
        user_service =  UserService(self.db)
        user = await user_service.get_raw_find_by_email(email)
        if not user:
            raise Exception(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        if not verify_password(password, user["password"]):
            raise Exception(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        role_service = RoleService(self.db)
        role = await role_service.get_role(user["role_id"])
        user_dump = await user_service.serialize(user)
        token_data = await get_token_data(user_dump, role)
        return generate_token_set(token_data)

    async def register_user(self, new_user: NewUser, background_tasks: BackgroundTasks) -> dict:
        user_service = UserService(self.db)
        existing_user = await user_service.find_by_email(new_user.email)
        if existing_user:
            raise Exception(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        role_service = RoleService(self.db)
        tenant_service = TenantService(self.db)

        hashed_password = get_password_hash(new_user.password)
        user_dict = new_user.model_dump().copy()
        user_dict["password"] = hashed_password
        user_dict["is_active"] = False  # User starts as inactive until activation
        guest_role = await role_service.find_by_name(RoleType.GUEST)
        user_dict["role_id"] = ObjectId(guest_role["id"])
        user_dict["created_at"] = datetime.utcnow()
        tenant_id = None

        if is_tenancy_enabled():
            logger.info("Multi-tenancy is enabled during user registration")
            sub_domain = user_dict['sub_domain']
            if sub_domain is None:
                raise Exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subdomain is required"
                )
            
            try:
                result = await tenant_service.create_tenant({
                    "name": sub_domain.split(".")[0],
                    "sub_domain": sub_domain
                })
                if result.inserted_id is None:
                    raise Exception(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create tenant"
                    )
                tenant_id = str(result.inserted_id)
                logger.info(f"Tenant created: {result.inserted_id}")
                user_dict["tenant_id"] = ObjectId(result.inserted_id)
                db = client[f"tenant_{tenant_id}"]
                user_service = UserService(db)
                tenant_seeder = SeedDataForNewlyCreatedTenant(db)
                background_tasks.add_task(tenant_seeder.fill_roles, user_dict["email"])
            except Exception as e:
                raise Exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
    
        result = await user_service.create_user(user_dict)

        if result.inserted_id:
            activation_email_data = ActivationEmailSchema(
                    email=user_dict["email"],
                    user_id=str(result.inserted_id),
                    first_name=user_dict["first_name"],
                    tenant_id=tenant_id if tenant_id is not None else None
                )
            background_tasks.add_task(send_activation_email, activation_email_data)
        else:
            raise Exception(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
            )

        if tenant_id is not None:
            tenant = await tenant_service.get_tenant(tenant_id)
            return {
                "tenant": tenant,
                "new_tenant_created": True
            }
        else:
            return {
                "tenant": None,
                "new_tenant_created": False
            }


    async def me(self, user_id: str):
        user_service = UserService(self.db)
        role_service = RoleService(self.db)
        user = await user_service.get_user(user_id)
        user["role"] = await role_service.get_role(user["role_id"])
        return user


    async def refresh_user_token(self, refresh_token: str):
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise Exception(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        user_service = UserService(self.db)
        user = await user_service.get_user(user_id)
        if user is None:
            raise Exception(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        role_service = RoleService(self.db)
        role = await role_service.get_role(user["role_id"])
        token_data = await get_token_data(user, role)
        return generate_token_set(token_data)
