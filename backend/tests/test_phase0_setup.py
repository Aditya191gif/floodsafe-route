"""Phase 0 Setup & Environment Verification Tests."""

from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.core.config import settings
from backend.app.main import app


def test_settings_load_correctly() -> None:
    """Verify application settings load with required pilot district defaults."""
    assert settings.APP_NAME == "FloodSafe Route"
    assert settings.DISTRICT_NAME == "Kanpur Nagar"
    assert settings.DISTRICT_STATE == "Uttar Pradesh"
    assert settings.TARGET_CRS == "EPSG:32644"

    min_lon, min_lat, max_lon, max_lat = settings.bbox_coords
    assert min_lon < max_lon
    assert min_lat < max_lat
    assert 80.0 <= min_lon <= 81.0
    assert 26.0 <= min_lat <= 27.0


def test_cors_origins_parsed() -> None:
    """Verify CORS origins string parses into clean list."""
    origins = settings.cors_origins
    assert isinstance(origins, list)
    assert len(origins) >= 1
    assert "http://localhost:5173" in origins


def test_project_structure_exists() -> None:
    """Verify required architecture directories and documentation exist."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    required_paths = [
        base_dir / "docs" / "STACK.md",
        base_dir / "docs" / "ARCHITECTURE.md",
        base_dir / "docs" / "DATA.md",
        base_dir / "docs" / "DECISIONS.md",
        base_dir / "docs" / "SIH_PITCH.md",
        base_dir / "requirements.txt",
        base_dir / "backend" / "requirements.txt",
        base_dir / "frontend" / "package.json",
        base_dir / ".env.example",
        base_dir / ".gitignore",
    ]
    for p in required_paths:
        assert p.exists(), f"Missing required file: {p}"


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    """Verify FastAPI /health endpoint returns HTTP 200 with district info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "FloodSafe Route"
        assert data["pilot_district"]["name"] == "Kanpur Nagar"
        assert data["pilot_district"]["crs"] == "EPSG:32644"
