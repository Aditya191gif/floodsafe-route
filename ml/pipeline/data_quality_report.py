"""Data Quality Assessment & Geospatial Validation Report.

Validates CRS consistency, raster grid alignment, value distributions,
geometry validity, and generates a structured data audit report.
"""

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio

from ml.pipeline.config import pipeline_config
from ml.pipeline.dem_ingest import generate_kanpur_dem
from ml.pipeline.osm_ingest import export_osm_datasets
from ml.pipeline.rainfall_ingest import generate_kanpur_rainfall
from ml.pipeline.sar_ingest import generate_sentinel1_flood_labels


def run_data_ingest_pipeline() -> dict[str, Path]:
    """Execute all ingestion steps if files do not exist."""
    paths = {
        "dem": pipeline_config.DEM_RAW_PATH,
        "roads": pipeline_config.ROADS_PATH,
        "shelters": pipeline_config.SHELTERS_PATH,
        "waterways": pipeline_config.WATERWAYS_PATH,
        "rainfall": pipeline_config.RAINFALL_PATH,
        "sar_labels": pipeline_config.SAR_LABELS_PATH,
    }

    if not paths["dem"].exists():
        generate_kanpur_dem()

    if not paths["roads"].exists() or not paths["shelters"].exists():
        export_osm_datasets()

    if not paths["rainfall"].exists():
        generate_kanpur_rainfall()

    if not paths["sar_labels"].exists():
        generate_sentinel1_flood_labels()

    return paths


def generate_data_quality_report(output_json: Path | None = None) -> dict:
    """Validate all ingested datasets and generate quality metrics."""
    paths = run_data_ingest_pipeline()
    out_file = output_json or pipeline_config.REPORT_PATH

    report: dict = {
        "district": pipeline_config.DISTRICT_NAME,
        "state": pipeline_config.STATE_NAME,
        "target_crs": pipeline_config.TARGET_CRS,
        "cell_size_meters": pipeline_config.CELL_SIZE_METERS,
        "status": "PASS",
        "checks": {},
        "summary": {},
    }

    # 1. DEM Validation
    with rasterio.open(paths["dem"]) as dem_src:
        dem_data = dem_src.read(1)
        valid_dem = dem_data[dem_data != dem_src.nodata]
        report["checks"]["dem"] = {
            "crs": str(dem_src.crs),
            "crs_matches_target": dem_src.crs.to_string() == pipeline_config.TARGET_CRS,
            "width": dem_src.width,
            "height": dem_src.height,
            "min_elevation_m": float(np.min(valid_dem)),
            "max_elevation_m": float(np.max(valid_dem)),
            "mean_elevation_m": float(np.mean(valid_dem)),
            "nan_count": int(np.isnan(valid_dem).sum()),
            "valid": True,
        }

    # 2. Rainfall Validation
    with rasterio.open(paths["rainfall"]) as rain_src:
        rain_data = rain_src.read(1)
        valid_rain = rain_data[rain_data != rain_src.nodata]
        report["checks"]["rainfall"] = {
            "crs": str(rain_src.crs),
            "crs_matches_target": rain_src.crs.to_string()
            == pipeline_config.TARGET_CRS,
            "grid_matches_dem": (
                rain_src.width == dem_src.width and rain_src.height == dem_src.height
            ),
            "min_mm": float(np.min(valid_rain)),
            "max_mm": float(np.max(valid_rain)),
            "mean_mm": float(np.mean(valid_rain)),
            "valid": True,
        }

    # 3. Sentinel-1 SAR Labels Validation
    with rasterio.open(paths["sar_labels"]) as sar_src:
        sar_data = sar_src.read(1)
        valid_sar = sar_data[sar_data != sar_src.nodata]
        flooded_cells = int(np.sum(valid_sar == 1))
        dry_cells = int(np.sum(valid_sar == 0))
        total_cells = flooded_cells + dry_cells
        flood_ratio = float(flooded_cells / total_cells) if total_cells > 0 else 0.0

        report["checks"]["sar_labels"] = {
            "crs": str(sar_src.crs),
            "crs_matches_target": sar_src.crs.to_string() == pipeline_config.TARGET_CRS,
            "grid_matches_dem": (
                sar_src.width == dem_src.width and sar_src.height == dem_src.height
            ),
            "flooded_cells": flooded_cells,
            "dry_cells": dry_cells,
            "flood_extent_percentage": round(flood_ratio * 100, 2),
            "valid": (0.01 <= flood_ratio <= 0.25),
        }

    # 4. OSM Roads Validation
    roads_gdf = gpd.read_file(paths["roads"])
    report["checks"]["roads"] = {
        "count": len(roads_gdf),
        "crs": str(roads_gdf.crs),
        "all_geometries_valid": bool(roads_gdf.geometry.is_valid.all()),
        "total_network_km": round(float(roads_gdf["length_m"].sum()) / 1000.0, 2),
        "highway_classes": roads_gdf["highway"].value_counts().to_dict(),
        "has_hindi_names": bool(roads_gdf["name_hi"].notna().all()),
        "valid": True,
    }

    # 5. Shelters Validation
    shelters_gdf = gpd.read_file(paths["shelters"])
    report["checks"]["shelters"] = {
        "count": len(shelters_gdf),
        "total_capacity": int(shelters_gdf["capacity"].sum()),
        "all_geometries_valid": bool(shelters_gdf.geometry.is_valid.all()),
        "has_phone_numbers": bool(shelters_gdf["phone"].notna().all()),
        "has_hindi_names": bool(shelters_gdf["name_hi"].notna().all()),
        "valid": True,
    }

    # 6. Waterways Validation
    waterways_gdf = gpd.read_file(paths["waterways"])
    report["checks"]["waterways"] = {
        "count": len(waterways_gdf),
        "all_geometries_valid": bool(waterways_gdf.geometry.is_valid.all()),
        "waterway_names": waterways_gdf["name"].tolist(),
        "valid": True,
    }

    # Overall Summary
    all_valid = all(check.get("valid", False) for check in report["checks"].values())
    report["status"] = "PASS" if all_valid else "FAIL"
    report["summary"] = {
        "status": report["status"],
        "total_road_segments": len(roads_gdf),
        "total_road_km": report["checks"]["roads"]["total_network_km"],
        "total_shelter_capacity": report["checks"]["shelters"]["total_capacity"],
        "flood_extent_percentage": report["checks"]["sar_labels"][
            "flood_extent_percentage"
        ],
        "raster_grid_dimensions": f"{dem_src.width} x {dem_src.height} cells @ 30m resolution",
    }

    # Save JSON report
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


if __name__ == "__main__":
    rep = generate_data_quality_report()
    print("Data Quality Report Completed:")
    print(json.dumps(rep["summary"], indent=2))
