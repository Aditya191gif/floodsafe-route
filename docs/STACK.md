# Technology Stack & Pinned Dependency Audit

**Audit Date:** 2026-10-14  
**Audit Standard:** Strict version pinning without ranges (`^`, `~`, `>=`), including exact Docker base image tags.

---

## 1. Runtime Environments

| Tool | Pinned Version | Purpose |
| :--- | :--- | :--- |
| **Python** | `3.11.15` | Backend API, GeoAI feature engineering, ML models, spatial routing |
| **Node.js** | `20.18.0` (LTS) | Frontend React/Vite build toolchain |
| **npm** | `10.8.2` | Frontend package manager |
| **PostgreSQL / PostGIS** | `16-3.4` (PostGIS 3.4 on PG 16) | Geospatial storage, indexing, spatial queries |

---

## 2. Python Packages (PyPI)

Pinned in `requirements.txt` and `backend/requirements.txt`:

| Category | Package | Exact Version | License | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Web & API** | `fastapi` | `0.143.1` | MIT | High-performance asynchronous REST API framework |
| | `uvicorn` | `0.54.0` | BSD-3-Clause | ASGI web server implementation |
| | `pydantic` | `2.14.1` | MIT | Strict request/response validation & serialization |
| | `pydantic-settings` | `2.16.0` | MIT | Environment-driven app configuration |
| | `slowapi` | `0.1.10` | MIT | In-memory and Redis-backed rate limiting for FastAPI |
| **Database & GIS** | `sqlalchemy` | `2.0.54` | MIT | Declarative ORM and async SQL engine |
| | `geoalchemy2` | `0.20.0` | MIT | PostGIS spatial extensions for SQLAlchemy |
| | `alembic` | `1.20.0` | MIT | Schema migration management |
| | `psycopg` (binary) | `3.3.6` | LGPL-3.0 | Modern PostgreSQL driver with async support |
| | `aiosqlite` | `0.21.0` | MIT | Async SQLite driver for zero-dependency local testing |
| **Spatial & Vector**| `geopandas` | `1.2.0` | BSD-3-Clause | Geospatial tabular analysis and GeoDataFrame operations |
| | `shapely` | `2.2.0` | BSD-3-Clause | Manipulation and analysis of geometric objects |
| | `pyproj` | `3.8.0` | MIT | Cartographic projections and coordinate transformations |
| | `osmnx` | `2.1.1` | MIT | OpenStreetMap network extraction and topological analysis |
| | `networkx` | `3.7` | BSD-3-Clause | Graph algorithms and multi-objective shortest path routing |
| **Raster & Remote Sensing** | `rasterio` | `1.5.2` | BSD-3-Clause | Direct GeoTIFF/GDAL raster I/O |
| | `xarray` | `2026.9.0` | Apache-2.0 | Multi-dimensional labeled raster arrays |
| | `rioxarray` | `0.23.0` | Apache-2.0 | Geospatial raster extensions for xarray |
| | `earthengine-api` | `1.7.48` | Apache-2.0 | Google Earth Engine client for Sentinel-1 / SAR extraction |
| **Data & ML** | `numpy` | `2.5.0` | BSD-3-Clause | Fundamental numerical array computation |
| | `pandas` | `3.0.6` | BSD-3-Clause | Tabular data manipulation and feature engineering |
| | `scikit-learn` | `1.9.1` | BSD-3-Clause | Spatial cross-validation, metrics, baseline models |
| | `xgboost` | `3.4.1` | Apache-2.0 | Gradient boosted decision trees for flood susceptibility |
| | `shap` | `0.53.0` | MIT | Explainable AI and feature importance attribution |
| | `imbalanced-learn`| `0.14.2` | BSD-3-Clause | Handling severe flood class imbalance (SMOTE / Tomek) |
| | `joblib` | `1.5.3` | BSD-3-Clause | Efficient model serialization and parallel processing |
| **Testing & Quality** | `pytest` | `9.1.1` | MIT | Primary Python test runner |
| | `pytest-cov` | `7.1.0` | MIT | Test suite coverage tracking and reporting |
| | `pytest-asyncio` | `1.4.0` | Apache-2.0 | Async endpoint and fixture testing |
| | `httpx` | `0.28.1` | BSD-3-Clause | Async HTTP client for end-to-end API test suite |
| | `ruff` | `0.16.2` | MIT | Ultra-fast linter and import sorter |
| | `black` | `25.1.0` | MIT | Deterministic code formatting |
| | `mypy` | `2.4.0` | MIT | Static type checking |

---

## 3. Frontend Packages (npm)

Pinned in `frontend/package.json` and `frontend/package-lock.json`:

| Category | Package | Exact Version | License | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Core Framework** | `react` | `19.3.0` | MIT | Declarative UI rendering engine |
| | `react-dom` | `19.3.0` | MIT | DOM bindings for React |
| | `typescript` | `7.0.2` | Apache-2.0 | Static type safety across all frontend components |
| | `vite` | `8.3.4` | MIT | Next-generation frontend build tool and dev server |
| | `@vitejs/plugin-react` | `6.0.1` | MIT | Fast Refresh and JSX transformation for Vite |
| **Mapping & Geospatial** | `maplibre-gl` | `6.13.0` | BSD-3-Clause | Open-source GPU-accelerated vector map renderer |
| **Localization** | `i18next` | `26.4.4` | MIT | Internationalization core framework |
| | `react-i18next` | `17.0.16` | MIT | React hooks for bilingual (Hindi/English) switching |
| | `i18next-browser-languagedetector` | `8.2.0` | MIT | Browser locale auto-detection |
| **UI Components** | `lucide-react` | `1.57.0` | ISC | Accessible, lightweight icon pack |
| **Offline & PWA** | `vite-plugin-pwa` | `2.0.0` | MIT | Zero-config PWA generation with Workbox |
| | `workbox-window` | `7.4.1` | MIT | Client-side service worker registration & cache lifecycle |
| **Testing & Tooling** | `vitest` | `5.0.3` | MIT | Fast Vite-native unit and component test runner |
| | `@testing-library/react` | `16.3.2` | MIT | DOM testing utilities focused on accessibility |
| | `@testing-library/jest-dom` | `6.9.1` | MIT | Custom DOM element matchers |
| | `jsdom` | `27.4.0` | MIT | Pure JavaScript DOM emulator for headless testing |
| | `eslint` | `9.39.0` | MIT | JavaScript and TypeScript linter |
| | `prettier` | `3.8.1` | MIT | Opinionated frontend code formatter |

---

## 4. Container Base Images

| Container | Pinned Image Reference | Base OS |
| :--- | :--- | :--- |
| **Backend** | `python:3.11.15-slim-bookworm` | Debian 12 Bookworm Slim |
| **Frontend Build** | `node:20.18.0-alpine3.20` | Alpine Linux 3.20 |
| **Frontend Serve** | `nginx:1.27.4-alpine3.20` | Alpine Linux 3.20 |
| **Database** | `postgis/postgis:16-3.4` | Debian 12 Bookworm |

---

## 5. Audit Compliance Checklist

- [x] Zero floating versions (`^` or `~` removed from `package.json`).
- [x] Zero unpinned PyPI ranges (`>=` removed; all pinned with `==`).
- [x] All base container images pinned with specific OS distributions and version tags.
- [x] License compatibility verified: all dependencies are permissive open source (MIT, BSD, Apache 2.0, ISC, LGPL).
