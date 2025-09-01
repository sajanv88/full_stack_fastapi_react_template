from fastapi import BackgroundTasks, Depends, APIRouter, status, HTTPException, Response
from jwt import InvalidTokenError
import jwt
from datetime import datetime
from pydantic import BaseModel
from app.core.db import user_collection, role_collection
from app.models.user import NewUser, User
from app.models.role import Role
from app.schemas.role_schema import serialize_role_schema
from bson import ObjectId
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.token import TokenSet, verify_refresh_token, verify_token, TokenData, generate_token_set
from app.schemas.user_schema import seralize_user_schema
from app.core.password import get_password_hash, verify_password
from app.core.smtp_email import ActivationEmailSchema, send_activation_email, verify_activation_token



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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", refreshUrl="api/auth/refresh")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
        token_data = TokenData(email=payload["email"], sub=payload["sub"], role=payload["role"])
    except InvalidTokenError:
        raise credentials_exception
    user = await user_collection.find_one({"_id": ObjectId(token_data.sub)})
    if user is None:
        raise credentials_exception
    return user


async def get_token_data(user):
    token_data = {"sub": str(user["_id"]), "email": user["email"]}.copy()
    if user["role_id"]:
        role = await role_collection.find_one({"_id": user["role_id"]})
        token_data["role"] = serialize_role_schema(role)

    return token_data

 
@router.post("/login", response_model=TokenSet)
async def login(login_request: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await user_collection.find_one({"email": login_request.username})
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
    token_data = await get_token_data(user)
    return generate_token_set(token_data)


@router.post("/register", response_class=Response)
async def register(background_tasks: BackgroundTasks, new_user: NewUser):
    existing_user = await user_collection.find_one({"email": new_user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(new_user.password)
    user_dict = new_user.model_dump().copy()
    user_dict["password"] = hashed_password
    user_dict["is_active"] = False  # User starts as inactive until activation
    
    result = await user_collection.insert_one(user_dict)
    if result.inserted_id:
        activation_email_data = ActivationEmailSchema(
                email=user_dict["email"],
                user_id=str(result.inserted_id),
                first_name=user_dict["first_name"]
            )

        background_tasks.add_task(send_activation_email, activation_email_data)
        return Response(status_code=status.HTTP_201_CREATED)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )
    

@router.get("/me", response_model=UserMeResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    user = seralize_user_schema(current_user)
    if current_user['role_id']:
        role = await role_collection.find_one({"_id": ObjectId(current_user["role_id"])})
        user["role"] = serialize_role_schema(role)

    return user


@router.post("/refresh", response_model=TokenSet)
async def refresh_token(token: RefreshRequest):
    try:
        refresh_token = token.refresh_token
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        token_data = await get_token_data(user)
        return generate_token_set(token_data)
    except InvalidTokenError:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
            )


@router.post("/activate")
async def activate_account(request: ActivationRequest):
    """
    Activate user account using the activation token.
    """
    try:
        # Verify the activation token
        token_data = verify_activation_token(request.token)
        user_id = token_data.get("user_id")
        email = token_data.get("email")
        
        # Find the user in the database
        user = await user_collection.find_one({"_id": ObjectId(user_id), "email": email})
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
        await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": True, "activated_at": datetime.utcnow()}}
        )
        
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
