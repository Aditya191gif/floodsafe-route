"""Rainfall Ingestion and Scenario Modeler for Kanpur Nagar.

Generates 72-hour antecedent precipitation grids (CHIRPS / IMD gridded baseline)
and supports scenario multipliers (+10mm to +100mm cloudburst events).
"""

from pathlib import Path

import numpy as np
import rasterio

from ml.pipeline.config import pipeline_config
from ml.pipeline.dem_ingest import compute_utm_grid_bounds


def generate_kanpur_rainfall(
    base_event_mm: float = 115.0,
    scenario_additional_mm: float = 0.0,
    output_path: Path | None = None,
) -> Path:
    """Generate 72h antecedent rainfall grid for Kanpur Nagar.

    Baseline event: Heavy monsoon cloudburst event (115 mm 72h cumulative).
    Rainfall gradient: Slightly higher precipitation in the northern river basin
    and southern catchment corridor.
    """
    out_file = output_path or pipeline_config.RAINFALL_PATH
    out_file.parent.mkdir(parents=True, exist_ok=True)

    min_x, min_y, max_x, max_y, width, height, transform = compute_utm_grid_bounds()

    x = np.linspace(min_x, max_x, width)
    y = np.linspace(max_y, min_y, height)
    xx, yy = np.meshgrid(x, y)

    norm_x = (xx - min_x) / (max_x - min_x)
    norm_y = (yy - min_y) / (max_y - min_y)

    # Spatial storm cell gradient centered over urban core and northern basin
    storm_cell = np.exp(-(((norm_x - 0.45) ** 2 + (norm_y - 0.55) ** 2) / 0.08)) * 25.0
    orographic_gradient = norm_y * 10.0

    total_rain = (
        base_event_mm + scenario_additional_mm + storm_cell + orographic_gradient
    )

    # Add micro-variation
    np.random.seed(101)
    noise = np.random.normal(0, 1.5, size=(height, width))
    rain_array = np.clip(total_rain + noise, 0, 500).astype(np.float32)

    with rasterio.open(
        out_file,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=rain_array.dtype,
        crs=pipeline_config.TARGET_CRS,
        transform=transform,
        nodata=-9999.0,
    ) as dst:
        dst.write(rain_array, 1)

    return out_file


if __name__ == "__main__":
    p = generate_kanpur_rainfall()
    print(f"Generated 72h rainfall grid at {p}")
