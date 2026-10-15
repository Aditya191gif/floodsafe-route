# System Architecture & Technical Specifications

**Project:** FloodSafe Route  
**Domain:** AI, GIS and Emerging Technologies (Smart India Hackathon 2026)  
**Pilot District:** Kanpur Nagar, Uttar Pradesh, India (`EPSG:32644` UTM Zone 44N)

---

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph Data Layer [1. Spatial Data Layer (Free & Open Data)]
        DEM[Copernicus DEM 30m / SRTM]
        OSM[OSM Highway & Shelters via OSMnx]
        S1[Sentinel-1 SAR Flood Masks GEE]
        RAIN[CHIRPS / GPM IMERG 24h & 72h]
    end

    subgraph Feature Pipeline [2. GeoAI Feature Engineering (EPSG:32644)]
        DEM --> TWI[Topographic Wetness Index ln a / tan beta]
        DEM --> SLOPE[Slope & Elevation Gradient]
        DEM --> FLOW[Flow Accumulation & Depressions]
        OSM --> DIST_RIVER[Euclidean Distance to Ganges / Canals]
        RAIN --> RAIN_FEAT[Rainfall Intensity & Antecedent Wetness]
        S1 --> LABELS[Binary Flood Extent Ground Truth]
    end

    subgraph ML Pipeline [3. Spatial ML Model]
        TWI & SLOPE & FLOW & DIST_RIVER & RAIN_FEAT & LABELS --> BLOCK_CV[Spatial Block Cross-Validation]
        BLOCK_CV --> XGB[Calibrated XGBoost Classifier]
        XGB --> CELL_PROB[30m Cell Flood Susceptibility Map]
    end

    subgraph Aggregation [4. Road Risk & Graph Engine]
        CELL_PROB & OSM --> EDGE_RISK[Road Segment Aggregator: Mean + Max Risk]
        EDGE_RISK --> NET_GRAPH[Dual-Objective NetworkX Graph]
        CITIZEN_REP[Citizen Waterlogging Reports] -->|Decay Penalty| NET_GRAPH
    end

    subgraph Backend API [5. FastAPI Service & PostGIS]
        NET_GRAPH --> FASTAPI[FastAPI Asynchronous Engine]
        FASTAPI <--> DB[(PostgreSQL 16 + PostGIS / SQLite SpatiaLite)]
        FASTAPI --> API_ROUTE[/route: Fastest vs Safest]
        FASTAPI --> API_EVAC[/evacuate: Nearest Safe Shelter]
        FASTAPI --> API_RISK[/risk: GeoJSON Heatmap]
        FASTAPI --> API_REP[/reports: Citizen Reporting]
    end

    subgraph Frontend PWA [6. Progressive Web App (React 19 + MapLibre GL)]
        API_ROUTE & API_EVAC & API_RISK & API_REP --> MAP_UI[MapLibre GL GPU Vector Canvas]
        SLIDER[Safety vs Speed Slider alpha] --> MAP_UI
        SCENARIO[What-If Rainfall Slider +mm] --> MAP_UI
        I18N[Bilingual Toggle: English / हिन्दी] --> MAP_UI
        SW[Workbox Service Worker] -->|Tile & Risk Cache| MAP_UI
    end
```

---

## 2. Multi-Objective Routing Mathematics

Standard navigation engines compute the shortest path by minimizing travel time:
$$\min_{\mathcal{P}} \sum_{e \in \mathcal{P}} \text{travel\_time}(e)$$

FloodSafe Route introduces an adjustable safety penalty factor $\alpha \ge 0$:

$$\text{Cost}(e, \alpha) = \text{travel\_time}(e) \cdot \left(1 + \alpha \cdot \text{Risk}(e)^\gamma\right) + \sum_{r \in \mathcal{R}(e)} \text{Penalty}(r, t)$$

Where:
- $\text{travel\_time}(e) = \frac{\text{length}(e)}{\text{maxspeed}(e)}$ (derived from OSM road attributes).
- $\text{Risk}(e) \in [0.0, 1.0]$ is the calibrated flood probability predicted by the spatial GeoAI model for edge $e$.
- $\gamma = 2.0$ non-linearly penalizes moderate-to-severe flood risks.
- $\alpha \in [0.0, 10.0]$ is the user-controlled "Safety vs Speed" slider value:
  - When $\alpha = 0$: Cost equals pure travel time (yielding the **Fastest Route**).
  - When $\alpha > 0$: Flooded roads become heavily penalized, forcing routing algorithms (Dijkstra / A*) to discover the **Safest Route**.
- $\text{Penalty}(r, t)$ is the dynamic impedance from active citizen waterlogging reports:
  $$\text{Penalty}(r, t) = \beta \cdot \text{severity}(r) \cdot \max\left(0, 1 - \frac{t - t_r}{\Delta t_{\text{expiry}}}\right)$$

---

## 3. Database Schema (PostGIS & SQLite SpatiaLite)

### Table: `road_segments`
- `id`: Primary key (UUID/BigInt).
- `osm_id`: OSM edge reference.
- `name`: Street name (English + localized).
- `highway`: OSM road classification (`motorway`, `primary`, `secondary`, `residential`, etc.).
- `length_m`: Edge length in meters.
- `maxspeed_kph`: Speed limit or default for highway class.
- `base_flood_risk`: Float $[0, 1]$ predicted by GeoAI baseline.
- `current_flood_risk`: Float $[0, 1]$ including live rainfall adjustments.
- `geometry`: `LineString` in `EPSG:32644` (or WGS84 `EPSG:4326` for GeoJSON).

### Table: `shelters`
- `id`: Primary key.
- `name`: Facility name (e.g. Kanpur Cantonment General Hospital, GSVM Medical College).
- `type`: `hospital`, `school`, `community_center`, `relief_camp`.
- `capacity`: Integer estimated occupancy.
- `current_occupancy`: Integer current evacuees.
- `is_safe`: Boolean (verified flood safety index $\ge 0.85$).
- `geometry`: `Point` (`EPSG:4326`).

### Table: `citizen_reports`
- `id`: Primary key.
- `segment_id`: Foreign key referencing `road_segments.id`.
- `water_depth_cm`: Integer estimated depth ($0\text{--}150\text{cm}$).
- `impassable`: Boolean flag (true if blocked).
- `description`: Text notes.
- `upvotes`: Integer community verification count.
- `created_at`: UTC timestamp.
- `expires_at`: UTC timestamp (default $+3$ hours).
- `geometry`: `Point` (`EPSG:4326`).

---

## 4. API Endpoints Contract

| Method | Endpoint | Request Payload | Response Summary |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | — | System liveness, model version, DB connectivity |
| `POST` | `/api/v1/route` | `{origin: [lon, lat], destination: [lon, lat], safety_alpha: float}` | Dual route GeoJSON (Fastest + Safest) with time, distance, risk stats |
| `POST` | `/api/v1/evacuate` | `{origin: [lon, lat], preferred_type?: string}` | Safest route to nearest high-capacity, non-flooded shelter |
| `GET` | `/api/v1/risk` | `?bbox=minx,miny,maxx,maxy` | Road segment FeatureCollection with color-coded risk attributes |
| `POST` | `/api/v1/reports` | `{latitude, longitude, depth_cm, impassable, comment}` | Newly created report with snapped road segment ID and expiry |
| `GET` | `/api/v1/reports` | `?active_only=true` | Active citizen waterlogging points within pilot boundary |
| `POST` | `/api/v1/scenario` | `{rainfall_increase_mm: float}` | Recalculated pilot edge risk indices under simulated cloudburst |
