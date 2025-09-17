import logging
from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel
from typing import List, Optional
import os

logger = logging.getLogger(__name__)

import jwt
from datetime import datetime, timedelta, timezone

MAIL_USERNAME = os.getenv("SMTP_USER")
MAIL_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("SMTP_MAIL_FROM")
MAIL_FROM_NAME = os.getenv("SMTP_MAIL_FROM_NAME")
MAIL_PORT = os.getenv("SMTP_PORT")
MAIL_SERVER = os.getenv("SMTP_HOST")

# JWT settings for activation tokens
JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key")
ALGORITHM = "HS256"
ACTIVATION_TOKEN_EXPIRE_HOURS = 24  # Token expires in 24 hours
API_ENDPOINT_BASE = os.getenv("API_ENDPOINT_BASE")


MAIL_STARTTLS = os.getenv("SMTP_STARTTLS", False)
MAIL_SSL_TLS = os.getenv("SMTP_SSL_TLS", False)

class EmailSchema(BaseModel):
    email: List[EmailStr]

class ActivationEmailSchema(BaseModel):
    email: EmailStr
    user_id: str
    first_name: str
    tenant_id: Optional[str] = None
    jwt_secret: Optional[str] = None  # Used for password reset tokens



conf = ConnectionConfig(
    MAIL_USERNAME = MAIL_USERNAME,
    MAIL_PASSWORD = MAIL_PASSWORD,
    MAIL_FROM = MAIL_FROM,
    MAIL_PORT = MAIL_PORT,
    MAIL_SERVER = MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS = MAIL_STARTTLS,
    MAIL_SSL_TLS = MAIL_SSL_TLS,
    USE_CREDENTIALS = False, # Changed to True when running production env
    VALIDATE_CERTS = False,
)


def generate_activation_token(
        user_id: str,
        email: str,
        type: str,
        tenant_id: Optional[str] = None,
        jwt_secret: Optional[str] = None
) -> str:
    """
    Generate a JWT token for account activation.
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=ACTIVATION_TOKEN_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "type": type,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "tenant_id": tenant_id
    }
    token = jwt.encode(payload, jwt_secret or JWT_SECRET, algorithm=ALGORITHM)
    return token


def generate_activation_link(user_id: str, email: str, type: str, tenant_id: Optional[str] = None, jwt_secret: Optional[str] = None) -> str:
    """
    Generate a complete activation link with token.
    """
    token = generate_activation_token(user_id, email, type, tenant_id, jwt_secret)
    activation_link = f"{API_ENDPOINT_BASE}/v1/auth/{type}?user_id={user_id}&token={token}"
    return activation_link


def verify_activation_token(token: str) -> dict:
    """
    Verify and decode the activation token.
    Returns user_id and email if valid, raises exception if invalid.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get("type") != "activation":
            raise jwt.InvalidTokenError("Invalid token type")
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email")
        }
    except jwt.ExpiredSignatureError:
        logger.error("Activation token has expired")
        raise jwt.ExpiredSignatureError("Activation token has expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid activation token")
        raise jwt.InvalidTokenError("Invalid activation token")


def verify_password_reset_token(token: str, jwt_secret: str) -> dict:
    """
    Verify and decode the password reset token.
    Returns user_id and email if valid, raises exception if invalid.
    """
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=[ALGORITHM])
        logger.debug(f"Decoded password reset token payload: {payload}")
        if payload.get("type") != "password-reset-confirm":
            logger.debug(f"Invalid token type: {payload.get('type')}")
            raise jwt.InvalidTokenError("Invalid token type")
        return {
            "sub": payload.get("user_id"),
            "email": payload.get("email")
        }
    except jwt.ExpiredSignatureError:
        logger.error("Password reset token has expired")
        raise jwt.ExpiredSignatureError("Password reset token has expired")
    except jwt.InvalidTokenError:
        logger.error("Invalid password reset token")
        raise jwt.InvalidTokenError("Invalid password reset token")


async def send_activation_email(user_data: ActivationEmailSchema) -> JSONResponse:
    """
    Send an account activation email with activation link.
    """
    activation_link = generate_activation_link(user_data.user_id, user_data.email, "activation", user_data.tenant_id)

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Welcome to Full-Stack FastAPI React Template</h2>
        <p>Hello {user_data.first_name},</p>
        <p>Thank you for registering with us! To complete your registration and activate your account, please click the button below:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{activation_link}" 
               style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Activate Your Account
            </a>
        </div>
        
        <p>Or copy and paste this link in your browser:</p>
        <p style="word-break: break-all; color: #007bff;">{activation_link}</p>
        
        <p><strong>Note:</strong> This activation link will expire in 24 hours for security reasons.</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        <p style="font-size: 12px; color: #666;">
            If you didn't create an account with us, please ignore this email.
        </p>
    </div>
    """

    message = MessageSchema(
        subject="Activate Your Account - Full-Stack FastAPI React Template",
        recipients=[user_data.email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info(f"Activation email sent to {user_data.email}")
    return JSONResponse(status_code=200, content={
        "message": "Activation email has been sent", 
        "email": user_data.email
    })

async def send_email_change_activation(user_data: ActivationEmailSchema) -> JSONResponse:
    """
    Send an email change activation email with activation link.
    """
    activation_link = generate_activation_link(user_data.user_id, user_data.email, "email_change", user_data.tenant_id)
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Notification!</h2>
        <p>Hello {user_data.first_name},</p>
        <p>You have recently requested to change your email. Please click the button below to confirm your new email address:</p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{activation_link}" 
               style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Confirm Your New Email
            </a>
        </div>
        
        <p>Or copy and paste this link in your browser:</p>
        <p style="word-break: break-all; color: #007bff;">{activation_link}</p>
        
        <p><strong>Note:</strong> This activation link will expire in 24 hours for security reasons.</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        <p style="font-size: 12px; color: #666;">
            If you didn't create an account with us, please ignore this email.
        </p>
    </div>
    """

    message = MessageSchema(
        subject="Confirm Your New Email - Full-Stack FastAPI React Template",
        recipients=[user_data.email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info(f"Email change activation email sent to {user_data.email}")
    return JSONResponse(status_code=200, content={
        "message": "Email change activation email has been sent", 
        "email": user_data.email
    })


async def send_password_reset_email(user_data: ActivationEmailSchema) -> JSONResponse:
    """
    Send a password reset email with reset link.
    """
    logger.info(f"Password reset token created for user {user_data.user_id}")

    reset_link = generate_activation_link(
        user_id=user_data.user_id, 
        email=user_data.email, 
        type="password-reset-confirm",
        tenant_id=user_data.tenant_id, 
        jwt_secret=user_data.jwt_secret
    )
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Password Reset Request</h2>
        <p>Hello {user_data.first_name},</p>
        <p>We received a request to reset your password. Click the button below to reset it:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" 
               style="background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Reset Your Password
            </a>
        </div>
        
        <p>Or copy and paste this link in your browser:</p>
        <p style="word-break: break-all; color: #007bff;">{reset_link}</p>
        
        <p><strong>Note:</strong> This password reset link will expire in 24 hours for security reasons.</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        <p style="font-size: 12px; color: #666;">
            If you didn't request a password reset, please ignore this email.
        </p>
    </div>
    """

    message = MessageSchema(
        subject="Reset Your Password - Full-Stack FastAPI React Template",
        recipients=[user_data.email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info(f"Password reset email sent to {user_data.email}")
    return JSONResponse(status_code=200, content={
        "message": "Password reset email has been sent", 
        "email": user_data.email
    })


async def notify_password_change(user_data: ActivationEmailSchema) -> JSONResponse:
    """
    Notify user that their password has been changed.
    """
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #333;">Password Changed Successfully</h2>
        <p>Hello {user_data.first_name},</p>
        <p>This is a confirmation that your password has been successfully changed.</p>
        
        <p>If you did not make this change, please contact our support team immediately.</p>
        
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        <p style="font-size: 12px; color: #666;">
            If you didn't request a password change, please contact support immediately.
        </p>
    </div>
    """

    message = MessageSchema(
        subject="Your Password Has Been Changed - Full-Stack FastAPI React Template",
        recipients=[user_data.email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info(f"Password change notification email sent to {user_data.email}")
    return JSONResponse(status_code=200, content={
        "message": "Password change notification email has been sent", 
        "email": user_data.email
    })