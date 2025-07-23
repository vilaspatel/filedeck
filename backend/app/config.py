"""
Configuration management for the Content Manager application.
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = Field(default="Content Manager", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(env="SECRET_KEY")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Database
    database_type: str = Field(default="postgresql", env="DATABASE_TYPE")
    database_url: str = Field(env="DATABASE_URL")
    
    # Storage
    storage_type: str = Field(default="azure", env="STORAGE_TYPE")
    azure_storage_account_name: Optional[str] = Field(None, env="AZURE_STORAGE_ACCOUNT_NAME")
    azure_storage_account_key: Optional[str] = Field(None, env="AZURE_STORAGE_ACCOUNT_KEY")
    azure_storage_container_name: Optional[str] = Field(None, env="AZURE_STORAGE_CONTAINER_NAME")
    gcp_project_id: Optional[str] = Field(None, env="GCP_PROJECT_ID")
    gcp_bucket_name: Optional[str] = Field(None, env="GCP_BUCKET_NAME")
    gcp_credentials_path: Optional[str] = Field(None, env="GCP_CREDENTIALS_PATH")
    aws_access_key_id: Optional[str] = Field(None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(None, env="AWS_SECRET_ACCESS_KEY")
    aws_bucket_name: Optional[str] = Field(None, env="AWS_BUCKET_NAME")
    aws_region: Optional[str] = Field(None, env="AWS_REGION")
    local_storage_path: str = Field(default="./uploads", env="LOCAL_STORAGE_PATH")
    
    # Azure AD
    azure_tenant_id: Optional[str] = Field(None, env="AZURE_TENANT_ID")
    azure_client_id: Optional[str] = Field(None, env="AZURE_CLIENT_ID")
    azure_client_secret: Optional[str] = Field(None, env="AZURE_CLIENT_SECRET")
    azure_authority: str = Field(default="https://login.microsoftonline.com/", env="AZURE_AUTHORITY")
    azure_scope: str = Field(default="https://graph.microsoft.com/.default", env="AZURE_SCOPE")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    
    # File Upload
    max_file_size: int = Field(default=100, env="MAX_FILE_SIZE")  # MB
    allowed_file_types: List[str] = Field(
        default=["pdf", "doc", "docx", "txt", "xml", "json", "csv", "xlsx", "png", "jpg", "jpeg", "gif"],
        env="ALLOWED_FILE_TYPES"
    )
    chunk_size: int = Field(default=8192, env="CHUNK_SIZE")
    
    # Multi-tenancy
    enable_multi_tenancy: bool = Field(default=True, env="ENABLE_MULTI_TENANCY")
    default_tenant_id: str = Field(default="default", env="DEFAULT_TENANT_ID")
    
    # Security
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Health Check
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> any:
            if field_name in ('cors_origins', 'allowed_file_types'):
                return [x.strip() for x in raw_val.split(',')]
            return cls.json_loads(raw_val)


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings() 