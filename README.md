FloodSafe Route

AI-powered, road-level flood risk prediction and flood-aware safe routing, built as a Progressive Web App (PWA).

Team: Cooked n Coded (HSC|UP|00158) · Hackathon: Hack for Social Cause (MoYAS and IIT Bombay, VBYLD 2027) · State: Uttar Pradesh Theme: Disaster management and resilience

The problem

Flood alerts and flood maps are usually area-level, but floods affect individual roads. Commuters and ambulances get no road-level view of which roads are unsafe right now, and navigation apps optimise for speed while ignoring flood risk. People end up driving into flooded roads and emergency response is delayed.

Our solution

FloodSafe Route predicts flood risk for each road segment and uses it to suggest safer routes.

Road-level flood risk: an ML model scores flood susceptibility per area, mapped onto OpenStreetMap road segments.
Risk-aware routing: travel time plus a risk penalty, with a safety-versus-speed slider.
Evacuation mode: one-tap route to the nearest shelter or hospital.
Citizen reports: users report flooded roads; reports raise risk only temporarily while the model remains the base.
Hindi and English, installable PWA with an offline cache of the map and last risk layer.
How it works

Open data  ->  ML model  ->  Road risk  ->  Routing  ->  Web app (PWA)
Sentinel-1     XGBoost,      Cell risk      Travel time    Map, alerts,
terrain,       spatial       mapped to      + risk         reports,
rainfall,      validation,   OSM road       penalty;       offline
drainage       SHAP          segments       evacuation
Open data: Sentinel-1 radar flood extents (as labels), terrain, rainfall and drainage layers.
ML model: XGBoost with spatial cross-validation (to avoid inflated accuracy) and SHAP for explainability.
Road risk: area risk is mapped onto OpenStreetMap road segments.
Routing: NetworkX / OSMnx graph with edge cost = travel time + risk penalty.
Web app: FastAPI backend serving a PWA frontend.
Tech stack

Area	Tools
Backend / API	Python 3.11, FastAPI, Uvicorn, Pydantic, SQLAlchemy, Alembic
Geospatial	GeoPandas, Shapely, pyproj, OSMnx, NetworkX, Rasterio, xarray, Google Earth Engine API
Machine learning	XGBoost, SHAP, scikit-learn, imbalanced-learn, pandas, NumPy
Frontend	Installable web app (PWA)
Quality	pytest, Ruff, Black, mypy, pre-commit, GitHub Actions
Repository structure

backend/     API, routing logic, database models and tests
frontend/    PWA client (map, alerts, reports)
ml/          Flood susceptibility model training and evaluation
notebooks/   Exploration and experiments
data/        Datasets and processed layers
docs/        Project documentation
.github/workflows/   CI
Getting started

Requires Python 3.11 or later.

git clone https://github.com/Aditya191gif/floodsafe-route.git
cd floodsafe-route

# Option 1: uv (a uv.lock is included)
uv sync

# Option 2: pip
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env             # then edit values
Run the backend and frontend as described in backend/ and frontend/ (add the exact commands here once finalised).

Tests and code quality

pytest                           # runs tests in backend/tests
ruff check . && black --check .
pre-commit install
Impact

Fewer people trapped on flooded roads
Faster ambulance and emergency response
Safer daily commutes during monsoon
Scalable to other districts by changing the study area
Stakeholders: commuters and residents, ambulance and emergency services, district disaster management authorities, municipal and road agencies.

Limitations and honest metrics

Few labelled flood events, so Sentinel-1 flood extents are used as labels.
Model accuracy is reported with spatial cross-validation; results will be added here after evaluation on the pilot district.
Citizen reports can be wrong, so they only raise risk temporarily.
Data sources and references

Sentinel-1 mission (Copernicus/ESA)
OpenStreetMap
Chen and Guestrin (2016), XGBoost: A Scalable Tree Boosting System
Lundberg and Lee (2017), A Unified Approach to Interpreting Model Predictions (SHAP)
Team

Ayushi Pandey: Front/Backend, Designer
Aditya Tripathi: Model Trainer, Developer
Students of PSIT, Kanpur (affiliated to AKTU).

AI tools used

Gemini Pro, Claude and GitHub Copilot were used as development assistants.
