"""Data Pipeline Configuration for FloodSafe Route.

Pilot District: Kanpur Nagar, Uttar Pradesh, India
Target CRS: EPSG:32644 (UTM Zone 44N)
Resolution: 30m grid cells
"""

from pathlib import Path

from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)


class PipelineConfig(BaseSettings):
    """Pipeline configuration settings."""

    # Pilot District BBox: [min_lon, min_lat, max_lon, max_lat]
    # Covers urban Kanpur, Ganges riverfront, Kanpur Cantonment, and southern tributaries
    DISTRICT_NAME: str = "Kanpur Nagar"
    STATE_NAME: str = "Uttar Pradesh"
    MIN_LON: float = 80.15
    MIN_LAT: float = 26.35
    MAX_LON: float = 80.45
    MAX_LAT: float = 26.55

    # Target Coordinate Reference System (Metric UTM 44N)
    TARGET_CRS: str = "EPSG:32644"
    WGS84_CRS: str = "EPSG:4326"

    # Spatial resolution in meters
    CELL_SIZE_METERS: float = 30.0

    # Paths
    DEM_RAW_PATH: Path = RAW_DATA_DIR / "dem_kanpur_30m.tif"
    ROADS_PATH: Path = RAW_DATA_DIR / "osm_roads.geojson"
    SHELTERS_PATH: Path = RAW_DATA_DIR / "osm_shelters.geojson"
    WATERWAYS_PATH: Path = RAW_DATA_DIR / "osm_waterways.geojson"
    RAINFALL_PATH: Path = RAW_DATA_DIR / "rainfall_72h_kanpur.tif"
    SAR_LABELS_PATH: Path = RAW_DATA_DIR / "sentinel1_flood_labels.tif"
    REPORT_PATH: Path = DATA_DIR / "data_quality_report.json"

    @property
    def bbox_tuple(self) -> tuple[float, float, float, float]:
        """Return (min_lon, min_lat, max_lon, max_lat)."""
        return self.MIN_LON, self.MIN_LAT, self.MAX_LON, self.MAX_LAT


pipeline_config = PipelineConfig()
