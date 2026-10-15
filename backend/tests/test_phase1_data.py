"""Phase 1 Data Ingestion & Quality Verification Tests."""

import geopandas as gpd
import numpy as np
import pytest
import rasterio

from ml.pipeline.config import pipeline_config
from ml.pipeline.data_quality_report import (
    generate_data_quality_report,
    run_data_ingest_pipeline,
)


@pytest.fixture(scope="module")
def ingested_data():
    """Ensure data is ingested before tests run."""
    return run_data_ingest_pipeline()


def test_dem_raster_properties(ingested_data) -> None:
    """Verify DEM GeoTIFF CRS, resolution, and elevation distribution."""
    dem_path = ingested_data["dem"]
    assert dem_path.exists()

    with rasterio.open(dem_path) as src:
        assert src.crs.to_string() == pipeline_config.TARGET_CRS
        assert src.res == (
            pipeline_config.CELL_SIZE_METERS,
            pipeline_config.CELL_SIZE_METERS,
        )
        assert src.width > 500
        assert src.height > 500

        data = src.read(1)
        valid = data[data != src.nodata]
        # Kanpur plain elevations should be between 110m and 140m MSL
        assert 110.0 <= np.min(valid) <= 122.0
        assert 125.0 <= np.max(valid) <= 140.0
        assert np.isnan(valid).sum() == 0


def test_osm_roads_integrity(ingested_data) -> None:
    """Verify OSM road network topology, bilingual tags, and travel times."""
    roads_path = ingested_data["roads"]
    assert roads_path.exists()

    gdf = gpd.read_file(roads_path)
    assert len(gdf) >= 15
    assert gdf.geometry.is_valid.all()

    # Required columns
    required_cols = [
        "segment_id",
        "u",
        "v",
        "name",
        "name_hi",
        "highway",
        "maxspeed_kph",
        "length_m",
        "free_flow_travel_time_sec",
        "is_flood_prone_historical",
    ]
    for col in required_cols:
        assert col in gdf.columns

    # Verify key test segments exist
    juhi_seg = gdf[gdf["segment_id"] == "seg_juhi_submerged"]
    assert len(juhi_seg) == 1
    assert bool(juhi_seg["is_flood_prone_historical"].iloc[0]) is True

    flyover_seg = gdf[gdf["segment_id"] == "seg_govind_flyover"]
    assert len(flyover_seg) == 1
    assert bool(flyover_seg["is_flood_prone_historical"].iloc[0]) is False


def test_shelters_and_hospitals(ingested_data) -> None:
    """Verify emergency shelters and healthcare points."""
    shelters_path = ingested_data["shelters"]
    assert shelters_path.exists()

    gdf = gpd.read_file(shelters_path)
    assert len(gdf) >= 5
    assert gdf.geometry.geom_type.isin(["Point"]).all()
    assert (gdf["capacity"] > 0).all()
    assert gdf["phone"].str.startswith("+91").all()

    names = gdf["name"].tolist()
    assert any("GSVM Medical College" in name for name in names)
    assert any("Kanpur Cantonment General Hospital" in name for name in names)


def test_rainfall_grid_alignment(ingested_data) -> None:
    """Verify rainfall raster matches DEM dimensions and projection."""
    with rasterio.open(ingested_data["dem"]) as dem_src:
        dem_shape = dem_src.shape
        dem_transform = dem_src.transform

    with rasterio.open(ingested_data["rainfall"]) as rain_src:
        assert rain_src.crs.to_string() == pipeline_config.TARGET_CRS
        assert rain_src.shape == dem_shape
        assert rain_src.transform == dem_transform

        rain_data = rain_src.read(1)
        valid_rain = rain_data[rain_data != rain_src.nodata]
        assert 70.0 <= np.min(valid_rain) <= 250.0


def test_sar_flood_labels(ingested_data) -> None:
    """Verify Sentinel-1 flood labels are binary and reflect realistic inundation."""
    with rasterio.open(ingested_data["sar_labels"]) as sar_src:
        assert sar_src.crs.to_string() == pipeline_config.TARGET_CRS
        data = sar_src.read(1)
        unique_vals = np.unique(data[data != sar_src.nodata])
        assert set(unique_vals).issubset({0, 1})

        flooded = (data == 1).sum()
        total = (data != sar_src.nodata).sum()
        ratio = flooded / total
        assert 0.02 <= ratio <= 0.15, f"Unexpected flood ratio: {ratio}"


def test_data_quality_report_passes(tmp_path) -> None:
    """Verify full data quality audit script returns PASS."""
    out_json = tmp_path / "test_quality_report.json"
    rep = generate_data_quality_report(output_json=out_json)
    assert rep["status"] == "PASS"
    assert rep["checks"]["dem"]["valid"] is True
    assert rep["checks"]["sar_labels"]["valid"] is True
    assert rep["checks"]["roads"]["valid"] is True
    assert out_json.exists()
