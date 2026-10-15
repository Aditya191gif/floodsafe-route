"""FloodSafe Route FastAPI Application Entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Hyperlocal road-segment flood risk prediction and dynamic multi-objective "
        "safe routing engine for Smart India Hackathon 2026."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str | bool | dict]:
    """Liveness probe and system status check."""
    min_lon, min_lat, max_lon, max_lat = settings.bbox_coords
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "pilot_district": {
            "name": settings.DISTRICT_NAME,
            "state": settings.DISTRICT_STATE,
            "country": settings.DISTRICT_COUNTRY,
            "crs": settings.TARGET_CRS,
            "bbox": {
                "min_lon": min_lon,
                "min_lat": min_lat,
                "max_lon": max_lon,
                "max_lat": max_lat,
            },
        },
    }
