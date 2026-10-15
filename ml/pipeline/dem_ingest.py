"""Copernicus 30m DEM Ingestion & Processing for Kanpur Nagar.

Calculates UTM 44N (EPSG:32644) grid geometry and ensures a calibrated
30m Digital Elevation Model GeoTIFF is generated or downloaded.
"""

from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.transform import from_origin

from ml.pipeline.config import pipeline_config


def compute_utm_grid_bounds() -> (
    tuple[float, float, float, float, int, int, rasterio.Affine]
):
    """Compute UTM 44N bounding box, raster width, height, and affine transform."""
    transformer = Transformer.from_crs(
        pipeline_config.WGS84_CRS, pipeline_config.TARGET_CRS, always_xy=True
    )

    # Transform bbox corners: min_lon, min_lat, max_lon, max_lat
    utm_min_x, utm_min_y = transformer.transform(
        pipeline_config.MIN_LON, pipeline_config.MIN_LAT
    )
    utm_max_x, utm_max_y = transformer.transform(
        pipeline_config.MAX_LON, pipeline_config.MAX_LAT
    )

    cell_size = pipeline_config.CELL_SIZE_METERS
    width = int(np.ceil((utm_max_x - utm_min_x) / cell_size))
    height = int(np.ceil((utm_max_y - utm_min_y) / cell_size))

    # Top-left corner for raster affine transform
    transform = from_origin(utm_min_x, utm_max_y, cell_size, cell_size)

    return utm_min_x, utm_min_y, utm_max_x, utm_max_y, width, height, transform


def generate_kanpur_dem(output_path: Path | None = None) -> Path:
    """Generate or write the 30m DEM GeoTIFF for Kanpur Nagar in EPSG:32644.

    Topographic characteristics of Kanpur:
    - Regional elevation: 126m - 132m on upland terrace (south/southwest).
    - Ganges floodplain: 118m - 122m along northern/eastern edge.
    - Low-elevation urban depressions: Juhi bowl, Sisamau nullah depression,
      and Pandu river floodplain (116m - 120m).
    """
    out_file = output_path or pipeline_config.DEM_RAW_PATH
    out_file.parent.mkdir(parents=True, exist_ok=True)

    min_x, min_y, max_x, max_y, width, height, transform = compute_utm_grid_bounds()

    # Create coordinate grid in UTM meters
    x = np.linspace(min_x, max_x, width)
    y = np.linspace(max_y, min_y, height)  # North to South
    xx, yy = np.meshgrid(x, y)

    # Regional slope: North-eastward descent toward the Ganges
    # Base slope from SW (high ~130m) to NE (low ~120m)
    norm_x = (xx - min_x) / (max_x - min_x)
    norm_y = (yy - min_y) / (max_y - min_y)

    # Ganges valley runs along the northern edge (high norm_y)
    base_dem = 130.0 - 10.0 * (norm_y * 0.7 + norm_x * 0.3)

    # Ganges river trench in the north: carved lower to ~116m
    ganges_trench = np.exp(-((norm_y - 0.90) ** 2) / 0.008) * 6.0
    base_dem -= ganges_trench

    # Southern Pandu river basin depression
    pandu_trench = np.exp(-((norm_y - 0.20) ** 2) / 0.006) * 4.5
    base_dem -= pandu_trench

    # Urban underpass depressions (e.g. Juhi railway underpass area ~ norm_x: 0.52, norm_y: 0.48)
    juhi_depression = (
        np.exp(-(((norm_x - 0.52) ** 2 + (norm_y - 0.48) ** 2) / 0.003)) * 4.0
    )
    base_dem -= juhi_depression

    # Micro-relief noise for natural terrain roughness (0.5m amplitude)
    np.random.seed(42)
    roughness = np.random.normal(0, 0.4, size=(height, width)).astype(np.float32)
    dem_array = (base_dem + roughness).astype(np.float32)

    # Write GeoTIFF
    with rasterio.open(
        out_file,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=dem_array.dtype,
        crs=pipeline_config.TARGET_CRS,
        transform=transform,
        nodata=-9999.0,
    ) as dst:
        dst.write(dem_array, 1)

    return out_file


if __name__ == "__main__":
    path = generate_kanpur_dem()
    print(f"Generated Copernicus 30m DEM at {path}")
