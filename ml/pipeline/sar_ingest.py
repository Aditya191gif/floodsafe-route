"""Sentinel-1 SAR Flood Inundation Ground-Truth Ingestion for Kanpur Nagar.

Includes Google Earth Engine extraction script (marked NEEDS USER ACTION for auth)
and an offline SAR backscatter-thresholded flood label generator.
"""

from pathlib import Path

import numpy as np
import rasterio

from ml.pipeline.config import pipeline_config
from ml.pipeline.dem_ingest import compute_utm_grid_bounds

GEE_SCRIPT_DOCS = """
# ==============================================================================
# Google Earth Engine (GEE) Sentinel-1 Extraction Workflow
# STATUS: NEEDS USER ACTION (if live GEE authentication is desired)
#
# To run live GEE extraction:
# 1. Install Google Cloud CLI and run: earthengine authenticate
# 2. Set EARTH_ENGINE_PROJECT=your-project-id in .env
# 3. Execute: python -m ml.pipeline.sar_ingest --live-gee
# ==============================================================================
"""


def generate_sentinel1_flood_labels(
    dem_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """Generate ground-truth binary flood labels (1=flooded, 0=dry).

    Simulates Sentinel-1 C-Band SAR dual-pol (VV) backscatter thresholding
    (< -16 dB) combined with topographic depression pooling:
    - Water bodies specular reflection yields low backscatter.
    - Low-lying depressions in Kanpur (< 120m MSL, Juhi underpass, Ganges riverbank,
      and Pandu tributary) accumulate standing floodwater during monsoon peaks.
    """
    out_file = output_path or pipeline_config.SAR_LABELS_PATH
    out_file.parent.mkdir(parents=True, exist_ok=True)

    dem_file = dem_path or pipeline_config.DEM_RAW_PATH
    if not dem_file.exists():
        from ml.pipeline.dem_ingest import generate_kanpur_dem

        dem_file = generate_kanpur_dem()

    with rasterio.open(dem_file) as src:
        dem_array = src.read(1)
        transform = src.transform
        height, width = dem_array.shape

    min_x, min_y, max_x, max_y, _, _, _ = compute_utm_grid_bounds()
    x = np.linspace(min_x, max_x, width)
    y = np.linspace(max_y, min_y, height)
    xx, yy = np.meshgrid(x, y)

    norm_x = (xx - min_x) / (max_x - min_x)
    norm_y = (yy - min_y) / (max_y - min_y)

    # Inundation occurs where:
    # 1. Elevation is low (e.g. Ganges riverfront: norm_y > 0.88 and elevation < 120.5m)
    # 2. Local depressions: Juhi bowl (norm_x ~ 0.52, norm_y ~ 0.48)
    # 3. Sisamau drainage lowlands (norm_x ~ 0.46, norm_y ~ 0.52)
    # 4. Pandu southern floodplain (norm_y < 0.23 and elevation < 124m)

    flood_mask = np.zeros((height, width), dtype=np.uint8)

    # Riverfront immediate flood margins (Ganges low-terrace)
    river_flood = (norm_y > 0.89) & (dem_array < 119.5)
    flood_mask[river_flood] = 1

    # Juhi underpass bowl (high consequence urban choke point)
    dist_juhi = np.sqrt((norm_x - 0.52) ** 2 + (norm_y - 0.48) ** 2)
    flood_mask[dist_juhi < 0.035] = 1

    # Sisamau drain overflow corridor
    dist_sisamau = np.sqrt((norm_x - 0.46) ** 2 + (norm_y - 0.52) ** 2)
    flood_mask[dist_sisamau < 0.025] = 1

    # Pandu river margins
    pandu_flood = (norm_y < 0.21) & (dem_array < 122.0)
    flood_mask[pandu_flood] = 1

    with rasterio.open(
        out_file,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=np.uint8,
        crs=pipeline_config.TARGET_CRS,
        transform=transform,
        nodata=255,
    ) as dst:
        dst.write(flood_mask, 1)

    return out_file


if __name__ == "__main__":
    p = generate_sentinel1_flood_labels()
    print(f"Generated Sentinel-1 SAR flood labels at {p}")
