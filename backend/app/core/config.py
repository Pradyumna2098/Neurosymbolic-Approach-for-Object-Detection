"""Configuration settings for the FastAPI backend.

Uses Pydantic settings to load configuration from environment variables
and .env file. This is a prototype configuration using local filesystem storage.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = "Neurosymbolic Object Detection API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Settings - Allow Electron app and local development
    # Note: FastAPI's CORSMiddleware doesn't support wildcard ports.
    # For development, we allow common ports. Override via environment.
    # In production, set specific origins via CORS_ORIGINS env var.
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
    ]
    
    # For Electron apps using file:// protocol, use allow_origin_regex in middleware
    cors_allow_origin_regex: str = r"^(file://.*|http://localhost:\d+|http://127\.0\.0\.1:\d+)$"
    
    # Local Storage Paths (relative to project root)
    data_root: Path = Path("data")
    uploads_dir: Path = Path("data/uploads")
    jobs_dir: Path = Path("data/jobs")
    results_dir: Path = Path("data/results")
    visualizations_dir: Path = Path("data/visualizations")
    
    # File Upload Settings
    max_upload_size: int = 10 * 1024 * 1024  # 10 MB
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def ensure_directories(self) -> None:
        """Create all required data directories if they don't exist."""
        for directory in [
            self.data_root,
            self.uploads_dir,
            self.jobs_dir,
            self.results_dir,
            self.visualizations_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
