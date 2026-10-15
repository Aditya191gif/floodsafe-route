"""Application configuration settings using Pydantic Settings."""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings for FloodSafe Route application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "FloodSafe Route"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-me-to-a-secure-random-string-at-least-32-chars-long"

    # Pilot District (Configurable)
    DISTRICT_NAME: str = "Kanpur Nagar"
    DISTRICT_STATE: str = "Uttar Pradesh"
    DISTRICT_COUNTRY: str = "India"
    DISTRICT_BBOX: str = "80.15,26.35,80.45,26.55"  # min_lon, min_lat, max_lon, max_lat
    TARGET_CRS: str = "EPSG:32644"

    # Database
    DATABASE_URL: str = "sqlite:///./floodsafe_dev.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./floodsafe_dev.db"

    # Security & CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    REPORT_RATE_LIMIT_PER_HOUR: int = 10

    # Routing & Risk Parameters
    DEFAULT_SAFETY_ALPHA: float = 3.0
    MAX_SAFETY_ALPHA: float = 10.0
    CITIZEN_REPORT_EXPIRY_HOURS: int = 3
    CITIZEN_REPORT_RADIUS_METERS: float = 50.0

    # Optional Earth Engine
    EARTH_ENGINE_PROJECT: str | None = None

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def bbox_coords(self) -> tuple[float, float, float, float]:
        """Return bounding box as tuple (min_lon, min_lat, max_lon, max_lat)."""
        coords = [float(x.strip()) for x in self.DISTRICT_BBOX.split(",")]
        if len(coords) != 4:
            raise ValueError("DISTRICT_BBOX must contain exactly 4 comma-separated floats.")
        return coords[0], coords[1], coords[2], coords[3]

    @field_validator("TARGET_CRS")
    @classmethod
    def validate_crs(cls, v: str) -> str:
        """Validate EPSG formatting."""
        if not v.startswith("EPSG:"):
            raise ValueError("TARGET_CRS must start with 'EPSG:'")
        return v


settings = Settings()
