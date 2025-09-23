
from dotenv import load_dotenv
from pydantic import EmailStr, ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "myapp"

    jwt_secret: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

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

    model_config = ConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8"
    )
    
# Instantiate settings once
settings = Settings()

