# Smart India Hackathon 2026 — Submission Pack

**Theme:** AI, GIS and Emerging Technologies  
**Project Title:** FloodSafe Route (बाढ़ सुरक्षित मार्ग)  
**Tagline:** Hyperlocal Road-Segment Flood Susceptibility & Dynamic Multi-Objective Safe Routing

---

## 1. Competitive Novelty Matrix

| Feature | Google Maps | Google Flood Hub | ISRO Bhuvan / NDMA Sachet | **FloodSafe Route (Ours)** |
| :--- | :---: | :---: | :---: | :---: |
| **Granularity** | Traffic speed only (no flood depth) | River basin / gauge station | District / Tehsil warning polygon | **Individual OSM Road Segments (~30m)** |
| **Routing Cost Objective** | Fastest travel time only | No routing provided | No routing provided | **Dual-Objective: Fastest vs Safest (User Slider)** |
| **Evacuation Navigation** | Manual destination typing | None | Static list of camps | **1-Click Dynamic Route to Nearest Non-Flooded Shelter** |
| **Citizen Ground-Truthing**| Stale accident pins | None | SMS / App broadcast only | **Snapping waterlog reports with 3-hr decay & spam guard** |
| **What-If Rainfall Scenarios**| None | Pre-set hydrologic models | None | **Live Rainfall Slider (+20mm, +50mm cloudburst simulation)** |
| **Explainable AI (XAI)** | Black box | Proprietary neural net | Rule-based hydrological tables | **SHAP feature importance (TWI, slope, river proximity)** |
| **Language Inclusivity** | Basic UI translation | English / Regional text | English / Hindi | **Full English & Hindi (हिंदी) route alerts & directions** |
| **Offline Resilience** | Offline maps (no dynamic risk) | Web only | SMS fallback | **PWA with offline tile cache & cached risk layer** |

---

## 2. Two-Minute Live Demo Pitch Script

- **[0:00 - 0:20] The Problem:**  
  *"Every monsoon across India, standard navigation apps lead commuters and emergency vehicles directly into drowned underpasses and submerged riverine roads. Why? Because current apps optimize purely for speed, treating a road with 3 feet of water the exact same as a dry road until traffic comes to a dead halt."*
- **[0:20 - 0:50] The Innovation (Road-Level GeoAI):**  
  *"We built FloodSafe Route. Using Copernicus 30m DEM, Sentinel-1 SAR flood imagery, and hydrological indices like the Topographic Wetness Index, our calibrated XGBoost model predicts flood risk down to individual road segments in Kanpur Nagar."*
- **[0:50 - 1:20] Live Interaction (Fastest vs Safest):**  
  *"Watch this trip from Kanpur Cantonment to Collectorate. The fastest route (in blue) saves 4 minutes, but routes directly through a severe inundation zone with an 85% flood hazard index. As the driver drags the 'Safety vs Speed' slider, our routing engine immediately identifies an elevated bypass (in green) with near-zero flood risk."*
- **[1:20 - 1:45] Evacuation & Citizen Ground-Truthing:**  
  *"In a cloudburst emergency, one click on 'Evacuation Mode' routes the user to the nearest high-capacity, flood-safe hospital. And when a resident spots unexpected waterlogging, they submit a 10-second report that snaps to the road segment and updates route calculations across the city for the next 3 hours."*
- **[1:45 - 2:00] Impact & Portability:**  
  *"100% open data, zero paid APIs, fully bilingual in Hindi and English, and PWA-ready for offline connectivity. FloodSafe Route turns satellite intelligence into lifesaving street-level navigation."*

---

## 3. Ten-Slide Presentation Deck Outline

1. **Slide 1: Title & Team:** Project FloodSafe Route — Smart India Hackathon 2026.
2. **Slide 2: The Urban Inundation Crisis:** Why existing maps fail during monsoons (underpasses, trapped ambulances).
3. **Slide 3: Our Core Differentiator:** Road-segment risk scoring vs coarse regional flood bulletins.
4. **Slide 4: Data Engineering Pipeline:** Copernicus 30m DEM, Sentinel-1 SAR water masks, OSM topology, CHIRPS rainfall.
5. **Slide 5: GeoAI Model & Spatial Cross-Validation:** Why spatial block CV is mandatory to avoid autocorrelation leakage; honest AUC and Brier metrics.
6. **Slide 6: Dual-Objective Routing Mathematics:** Edge cost equation balancing travel time against flood impedance.
7. **Slide 7: Citizen Reporting & Temporal Decay:** Anti-spam spatial clustering and dynamic time-decay impedance.
8. **Slide 8: System Architecture & Tech Stack:** FastAPI, PostGIS, React 19, MapLibre GL, Workbox PWA.
9. **Slide 9: Live Demo & Kanpur Case Study:** 3 trip comparisons, What-If rainfall scenario, evacuation routing.
10. **Slide 10: Scalability & National Rollout Roadmap:** Configuration for 500+ Indian districts using automated OSMnx + open satellite pipelines.
