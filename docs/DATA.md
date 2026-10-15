# Data Sources, Licensing & Geospatial Metadata

**Project:** FloodSafe Route  
**Target District:** Kanpur Nagar, Uttar Pradesh, India  
**Bounding Box:** $[80.15^\circ\text{E}, 26.35^\circ\text{N}]$ to $[80.45^\circ\text{E}, 26.55^\circ\text{N}]$  
**Projected Coordinate Reference System (CRS):** `EPSG:32644` (WGS 84 / UTM Zone 44N)  
**Display / Web CRS:** `EPSG:4326` (WGS 84) / `EPSG:3857` (Web Mercator)

---

## 1. Primary Data Catalog

| Dataset | Provider / Source | Resolution | License | Date Range | Acquisition Method |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Copernicus DEM (GLO-30)** | European Space Agency (ESA) / OpenTopography | $30\text{m}$ | Open Access (Creative Commons CC BY 4.0) | 2021 static baseline | Direct GeoTIFF download via Planetary Computer / OpenTopography REST API; fallback via SRTM 30m. |
| **OpenStreetMap (OSM)** | OpenStreetMap Contributors | Vector (nodes, ways) | ODbL (Open Database License) | Live / 2026 snapshot | Downloaded via Python `osmnx` library (`drive` filter for vehicular network, amenities for hospitals and schools). |
| **Sentinel-1 SAR GRD** | European Space Agency (ESA) via Copernicus | $10\text{m}$ (resampled to $30\text{m}$) | Open Access (EU Copernicus terms) | 2020–2026 Monsoon seasons (July–September) | Extracted via `earthengine-api` using dual-polarization (VV/VH) backscatter thresholding ($\sigma_0 < -16\text{ dB}$). Pre-processed offline GeoTIFF bundled in `data/sample/`. |
| **CHIRPS Rainfall** | Climate Hazards Center (UCSB) | $0.05^\circ$ (~$5\text{km}$) resampled to $30\text{m}$ | Public Domain | Daily 2018–2026 | Cloud-optimized GeoTIFFs via CHC HTTP server and Google Earth Engine. |
| **ESA WorldCover 10m** | European Space Agency | $10\text{m}$ | CC BY 4.0 | 2021 | Global land cover raster (built-up, tree cover, water, croplands). |
| **Waterways & Basins** | OSM Waterways & HydroSHEDS (USGS/WWF) | 3 arc-second | Free for non-commercial / research | Static baseline | River centerlines (Ganges River, Pandu River, Lower Ganga Canal) extracted via OSMnx and HydroSHEDS flow network. |

---

## 2. Feature Definitions & Hydrological Equations

1. **Elevation ($Z$):** Extracted directly from Copernicus 30m DEM in meters above mean sea level.
2. **Slope ($\beta$ in degrees):** Calculated using Horn's algorithm on DEM raster cell gradients:
   $$\tan \beta = \sqrt{\left(\frac{\partial Z}{\partial x}\right)^2 + \left(\frac{\partial Z}{\partial y}\right)^2}$$
3. **Topographic Wetness Index ($\text{TWI}$):**
   $$\text{TWI} = \ln\left(\frac{a}{\tan \beta + \epsilon}\right)$$
   where $a$ is the specific upslope contributing area per unit contour length, and $\beta$ is local slope. High TWI identifies topographic depressions prone to water accumulation.
4. **Distance to River ($\text{Dist}_{\text{river}}$ in meters):** Euclidean distance from cell centroid to the nearest riverbank or perennial canal.
5. **Impervious Surface Ratio:** Built-up fraction within $100\text{m}$ circular moving window.
6. **Rainfall Antecedent Index (72h precipitation):** Cumulative rainfall in millimeters over the 3 days preceding the event.

---

## 3. Ground Truth Flood Labelling

Positive flood labels are generated from Sentinel-1 C-band Synthetic Aperture Radar (SAR) acquisitions over Kanpur during major Ganges flood events (notably late August / September floods).
- Water bodies show specular reflection, resulting in very low backscatter coefficient $\sigma_0$.
- A threshold filter $\sigma_0(\text{VV}) < -16.0\text{ dB}$ combined with a slope filter ($\text{slope} < 5^\circ$) produces the binary ground truth water mask ($1 = \text{flooded}, 0 = \text{dry}$).
- Permanent water bodies (Ganges main channel) are masked out using dry-season reference imagery so the model specifically learns seasonal and episodic road waterlogging.

---

## 4. Honest Pilot Limitations & Constraints

1. **Spatial Resolution:** At $30\text{m}$ grid resolution, narrow alleyways ($< 5\text{m}$) may inherit elevation from surrounding building roofs in raw DEMs unless hydro-enforced.
2. **SAR Urban Shadowing:** Tall buildings in dense old Kanpur neighborhoods (e.g. Chowk, General Ganj) cause radar layover and shadow, causing false negatives in narrow street canyons. This is mitigated by fusing TWI and citizen reporting.
3. **Class Imbalance:** In urban Kanpur, only $3\text{--}8\%$ of the geographic area experiences severe inundation even during heavy monsoons. Precision-Recall AUC (PR-AUC) and Brier calibration score are reported alongside ROC-AUC to prevent misleading metrics.
