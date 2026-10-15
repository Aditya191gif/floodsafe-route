# Architecture Decision Records (ADRs)

This document tracks all non-obvious engineering decisions, rationale, trade-offs, and consequences for the **FloodSafe Route** project.

---

## ADR 001: Strict Spatial Block Cross-Validation (Eliminating Spatial Autocorrelation Leakage)

- **Date:** 2026-10-14
- **Status:** Accepted
- **Context:** Standard random k-fold cross-validation randomly samples test pixels immediately adjacent to training pixels. Because topographical elevations, slope, and water depths are strongly spatially auto-correlated (Tobler’s First Law of Geography), random k-fold yields deceptively high AUC scores (>0.98) that fail catastrophically when deployed to unseen neighborhoods or catchments.
- **Decision:** Split the study area into spatially segregated rectangular blocks or spatial clusters using spatial block partitioning. All pixels in a spatial block are held out simultaneously during validation.
- **Consequences:** The reported AUC and F1 scores will appear lower and more conservative (e.g., 0.78–0.86), but reflect true operational generalization. This honesty is a core differentiator for the Smart India Hackathon jury.

---

## ADR 002: Dynamic Multi-Objective Routing Cost Function

- **Date:** 2026-10-14
- **Status:** Accepted
- **Context:** Pure travel-time routing routes motorists through submerged underpasses. Hard-blocking flooded roads can fail if minor waterlogging (<10 cm) is tolerable for high-clearance vehicles or emergency responders.
- **Decision:** Formulate edge traversal cost as:
  $$\text{Cost}(e) = \text{travel\_time}(e) \times \left(1 + \alpha \cdot \text{Risk}(e)^2\right) + \text{Penalty}_{\text{citizen}}(e)$$
  where $\alpha \in [0, 10]$ is dynamically controlled by the user's "Safety vs Speed" slider.
  - $\alpha = 0$: Returns standard fastest route.
  - $\alpha > 0$: Exponentially penalizes higher-risk segments, finding optimal detours.
- **Consequences:** Guarantees that the algorithm is always solvable (no graph disconnection errors unless every path is 100% blocked), while giving the user full agency.

---

## ADR 003: MapLibre GL JS as Primary Geospatial Client

- **Date:** 2026-10-14
- **Status:** Accepted
- **Context:** Mapbox requires paid API keys and credit cards after small quotas. Leaflet is 2D raster-oriented with poor performance when rendering 5,000+ vector road segment lines with dynamic colors.
- **Decision:** Use **MapLibre GL JS** (v6.13.0) with free CartoDB Positron / OSM raster & vector tiles.
- **Consequences:** 100% free, zero external API keys needed, WebGL GPU acceleration enables smooth 60fps rendering of thousands of risk-colored road segments and animated routes.

---

## ADR 004: Decoupled Data Pipeline with Bundled Fallback Slices

- **Date:** 2026-10-14
- **Status:** Accepted
- **Context:** Google Earth Engine requires authentication (`earthengine authenticate`) which cannot run autonomously in headless CI or without user manual browser intervention.
- **Decision:** Write fully functional, clean GEE extraction scripts, but bundle a pre-extracted, verified spatial raster slice of Kanpur Nagar in `data/sample/`. The pipeline automatically uses local data if GEE credentials are not supplied.
- **Consequences:** Zero blocking on API keys; automated test suites and fresh clones work immediately offline.

---

## ADR 005: Citizen Report Temporal Decay & Spatial Deduplication

- **Date:** 2026-10-14
- **Status:** Accepted
- **Context:** Urban flooding changes rapidly. A road reported waterlogged at 2:00 PM may drain by 5:00 PM. Allowing unverified reports indefinitely creates phantom hazards.
- **Decision:** Citizen waterlogging reports have a strict default expiry (3 hours). A decay function reduces the report's risk penalty over time:
  $$\text{Weight}(t) = \max\left(0, 1 - \frac{t - t_{\text{report}}}{\Delta t_{\text{expiry}}}\right)$$
  Reports within 50 meters submitted within 15 minutes are clustered to prevent spam.
- **Consequences:** Prevents stale data and malicious spam from permanently distorting city routing.
