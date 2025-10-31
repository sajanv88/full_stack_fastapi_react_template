
from dotenv import load_dotenv
from pydantic import EmailStr, ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra="allow"
    )
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "myapp"

    jwt_secret: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7 * 24 * 60 * 60

    algorithm: str = "HS256"
    refresh_algorithm: str = "HS512"
    refresh_token_secret: str

    admin_email: EmailStr = "admin@example.com"
    admin_password: str = "Test@123!"

    app_title: str = "Full-Stack FastAPI React Template"
    app_version: str = "0.1.0"

    api_endpoint_base: str = "http://localhost:8000/api"

    multi_tenancy_strategy: str = "header"
    
    host_main_domain: str = "fsrapp.com"
    host_main_domain_prefix: str = "demo"  # Prefix for subdomains, e.g., demo.fsrapp.com. Change as needed.

    redis_uri: str = "redis://localhost:6372"
    celery_result_backend: str = "redis://localhost:6372/0"
    celery_broker_url: str = "redis://localhost:6372/0"


    fastapi_env: str = "development"  # Options: "development", "production"

    smtp_user: str
    smtp_password: str
    smtp_host: str
    smtp_port: int
    smtp_mail_from_name: str = "FSR App"
    smtp_mail_from: EmailStr
    smtp_starttls: bool = False
    smtp_ssl_tls: bool = False
    smtp_use_credentials: bool = False # Changed to True when running production env
    smtp_validate_certs: bool = False

    ollama_host: str = "http://localhost:11434"

    
    # Coolify settings for deployment integration only used for domain setup
    coolify_enabled: bool = False
    coolify_api_url: str
    coolify_api_key: str
    coolify_application_id: str


    # AWS S3 settings for file uploads this belongs to the Host - level settings
    aws_region: str = "eu-central-1"
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_s3_bucket_name: str = "fsrapptest"

    # Stripe Settings for Billing and Payments - Host Level Settings
    stripe_api_key: str
    stripe_publishable_key: str
    stripe_secret_key: str

# Instantiate settings once
settings = Settings()

