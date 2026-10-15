"""OpenStreetMap Vector Ingestion for Kanpur Nagar.

Extracts/builds vehicular road network, emergency shelters/hospitals,
and river drainage waterways for routing and flood risk mapping.
"""

from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString, Point

from ml.pipeline.config import pipeline_config


def get_kanpur_waterways() -> gpd.GeoDataFrame:
    """Return major rivers and canals in Kanpur Nagar."""
    # Ganges River meandering along northern boundary, Pandu River in south, Lower Ganga Canal
    features = [
        {
            "osm_id": 1001,
            "name": "Ganges River",
            "name_hi": "गंगा नदी",
            "waterway": "river",
            "geometry": LineString(
                [
                    (80.15, 26.54),
                    (80.22, 26.52),
                    (80.30, 26.50),
                    (80.38, 26.47),
                    (80.45, 26.42),
                ]
            ),
        },
        {
            "osm_id": 1002,
            "name": "Pandu River",
            "name_hi": "पाण्डु नदी",
            "waterway": "river",
            "geometry": LineString(
                [
                    (80.18, 26.37),
                    (80.26, 26.39),
                    (80.34, 26.38),
                    (80.44, 26.36),
                ]
            ),
        },
        {
            "osm_id": 1003,
            "name": "Lower Ganga Canal",
            "name_hi": "निचली गंगा नहर",
            "waterway": "canal",
            "geometry": LineString(
                [
                    (80.16, 26.46),
                    (80.24, 26.44),
                    (80.32, 26.42),
                    (80.40, 26.39),
                ]
            ),
        },
    ]
    gdf = gpd.GeoDataFrame(features, crs=pipeline_config.WGS84_CRS)
    return gdf


def get_kanpur_shelters() -> gpd.GeoDataFrame:
    """Return emergency relief shelters, hospitals, and disaster centers in Kanpur Nagar."""
    shelters_data = [
        {
            "id": "hosp-1",
            "name": "GSVM Medical College & LLR Hospital (Hallet)",
            "name_hi": "जीएसवीएम मेडिकल कॉलेज एवं लाला लाजपत राय अस्पताल",
            "amenity": "hospital",
            "capacity": 1500,
            "elevation_type": "elevated",
            "phone": "+91-512-2535483",
            "geometry": Point(80.3120, 26.4785),
        },
        {
            "id": "hosp-2",
            "name": "Kanpur Cantonment General Hospital",
            "name_hi": "कानपुर छावनी सामान्य अस्पताल",
            "amenity": "hospital",
            "capacity": 800,
            "elevation_type": "high_ground",
            "phone": "+91-512-2381200",
            "geometry": Point(80.3650, 26.4520),
        },
        {
            "id": "hosp-3",
            "name": "Ursula Horsman Memorial (UHM) Hospital",
            "name_hi": "उर्सुला हॉर्समैन मेमोरियल अस्पताल",
            "amenity": "hospital",
            "capacity": 650,
            "elevation_type": "standard",
            "phone": "+91-512-2365412",
            "geometry": Point(80.3480, 26.4660),
        },
        {
            "id": "hosp-4",
            "name": "Regency Hospital Govind Nagar",
            "name_hi": "रीजेंसी अस्पताल गोविन्द नगर",
            "amenity": "hospital",
            "capacity": 500,
            "elevation_type": "standard",
            "phone": "+91-512-3081111",
            "geometry": Point(80.2890, 26.4420),
        },
        {
            "id": "shelter-1",
            "name": "Kanpur Civil Defense Relief Camp (Phool Bagh)",
            "name_hi": "कानपुर नागरिक सुरक्षा राहत शिविर (फूल बाग)",
            "amenity": "shelter",
            "capacity": 2000,
            "elevation_type": "elevated",
            "phone": "+91-512-2305000",
            "geometry": Point(80.3550, 26.4710),
        },
        {
            "id": "shelter-2",
            "name": "Govind Nagar Disaster Relief Community Center",
            "name_hi": "गोविन्द नगर आपदा राहत सामुदायिक केंद्र",
            "amenity": "community_centre",
            "capacity": 1200,
            "elevation_type": "high_ground",
            "phone": "+91-512-2294100",
            "geometry": Point(80.3010, 26.4350),
        },
        {
            "id": "shelter-3",
            "name": "Kalyanpur Stadium Disaster Camp",
            "name_hi": "कल्याणपुर स्टेडियम आपदा राहत शिविर",
            "amenity": "shelter",
            "capacity": 2500,
            "elevation_type": "high_ground",
            "phone": "+91-512-2570020",
            "geometry": Point(80.2450, 26.5050),
        },
    ]
    gdf = gpd.GeoDataFrame(shelters_data, crs=pipeline_config.WGS84_CRS)
    return gdf


def get_kanpur_road_network() -> gpd.GeoDataFrame:
    """Return comprehensive arterial and collector road network for Kanpur Nagar."""
    # Nodes in Kanpur:
    # N1: Kalyanpur (80.24, 26.51)
    # N2: Rawatpur Junction (80.29, 26.49)
    # N3: GSVM / Swaroop Nagar (80.31, 26.48)
    # N4: Civil Lines / Mall Road (80.35, 26.47)
    # N5: Phool Bagh / Bada Chauraha (80.36, 26.47)
    # N6: Kanpur Central Station (80.35, 26.45)
    # N7: Kanpur Cantonment (80.38, 26.44)
    # N8: Ganga Barrage / Shuklaganj bypass (80.32, 26.52)
    # N9: Juhi Underpass Area (80.33, 26.43) [KNOWN FLOOD PRONE]
    # N10: Kidwai Nagar (80.34, 26.42)
    # N11: Govind Nagar (80.29, 26.44)
    # N12: Fazalganj Industrial (80.30, 26.46)
    # N13: Vijay Nagar (80.27, 26.47)
    # N14: Barra Bypass (80.28, 26.41)
    # N15: Jajmau Ganges Bridge (80.42, 26.43)
    # N16: Sisamau Nullah Corridor (80.32, 26.46) [LOW ELEVATION]
    # N17: Elevated Bypass / GT Road Flyover (80.31, 26.46 to 80.35, 26.45) [SAFE ROUTE]

    roads = [
        # 1. GT Road Trunk (Kalyanpur to Central)
        {
            "segment_id": "seg_gt_01",
            "u": "Kalyanpur",
            "v": "Rawatpur",
            "name": "Grand Trunk Road (NH 19)",
            "name_hi": "ग्रांड ट्रंक रोड (एनएच 19)",
            "highway": "trunk",
            "maxspeed_kph": 60,
            "lanes": 4,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.24, 26.51), (80.29, 26.49)]),
        },
        {
            "segment_id": "seg_gt_02",
            "u": "Rawatpur",
            "v": "Swaroop_Nagar",
            "name": "GT Road - Rawatpur Section",
            "name_hi": "जीटी रोड - रावतपुर खंड",
            "highway": "trunk",
            "maxspeed_kph": 50,
            "lanes": 4,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.29, 26.49), (80.31, 26.48)]),
        },
        {
            "segment_id": "seg_mall_01",
            "u": "Swaroop_Nagar",
            "v": "Civil_Lines",
            "name": "Mall Road (Mahatma Gandhi Marg)",
            "name_hi": "माल रोड (महात्मा गांधी मार्ग)",
            "highway": "primary",
            "maxspeed_kph": 45,
            "lanes": 4,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.31, 26.48), (80.35, 26.47)]),
        },
        {
            "segment_id": "seg_mall_02",
            "u": "Civil_Lines",
            "v": "Phool_Bagh",
            "name": "Mall Road - Bada Chauraha Stretch",
            "name_hi": "माल रोड - बड़ा चौराहा",
            "highway": "primary",
            "maxspeed_kph": 40,
            "lanes": 4,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.35, 26.47), (80.36, 26.47)]),
        },
        # 2. Juhi Underpass Link (Direct fastest connection between Central & Kidwai Nagar, but SEVERELY FLOODED in rain)
        {
            "segment_id": "seg_juhi_submerged",
            "u": "Kanpur_Central",
            "v": "Juhi_Underpass",
            "name": "Juhi Railway Underpass Road",
            "name_hi": "जूही रेलवे अंडरपास मार्ग",
            "highway": "secondary",
            "maxspeed_kph": 40,
            "lanes": 2,
            "is_flood_prone_historical": True,  # High flood susceptibility!
            "geometry": LineString([(80.35, 26.45), (80.33, 26.43)]),
        },
        {
            "segment_id": "seg_juhi_kidwai",
            "u": "Juhi_Underpass",
            "v": "Kidwai_Nagar",
            "name": "Juhi - Kidwai Nagar Link",
            "name_hi": "जूही - किदवई नगर मार्ग",
            "highway": "secondary",
            "maxspeed_kph": 40,
            "lanes": 2,
            "is_flood_prone_historical": True,
            "geometry": LineString([(80.33, 26.43), (80.34, 26.42)]),
        },
        # 3. Elevated Safe Bypass (Govind Nagar Flyover - alternative route that avoids Juhi underpass)
        {
            "segment_id": "seg_govind_flyover",
            "u": "Kanpur_Central",
            "v": "Govind_Nagar",
            "name": "Govind Nagar Elevated Flyover Bypass",
            "name_hi": "गोविन्द नगर एलिवेटेड फ्लाईओवर बाईपास",
            "highway": "primary",
            "maxspeed_kph": 50,
            "lanes": 4,
            "is_flood_prone_historical": False,  # Elevated high-ground safe route
            "geometry": LineString([(80.35, 26.45), (80.32, 26.45), (80.29, 26.44)]),
        },
        {
            "segment_id": "seg_govind_kidwai",
            "u": "Govind_Nagar",
            "v": "Kidwai_Nagar",
            "name": "Govind Nagar to Kidwai Nagar Southern Link",
            "name_hi": "गोविन्द नगर - किदवई नगर दक्षिणी मार्ग",
            "highway": "primary",
            "maxspeed_kph": 45,
            "lanes": 4,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.29, 26.44), (80.34, 26.42)]),
        },
        # 4. Ganga Riverfront Road (Low-lying river valley corridor, flooded when river swells)
        {
            "segment_id": "seg_ganga_barrage",
            "u": "Rawatpur",
            "v": "Ganga_Barrage",
            "name": "Ganga Barrage Riverfront Highway",
            "name_hi": "गंगा बैराज रिवरफ्रंट मार्ग",
            "highway": "secondary",
            "maxspeed_kph": 50,
            "lanes": 2,
            "is_flood_prone_historical": True,
            "geometry": LineString([(80.29, 26.49), (80.32, 26.52)]),
        },
        {
            "segment_id": "seg_ganga_civil",
            "u": "Ganga_Barrage",
            "v": "Civil_Lines",
            "name": "VIP Road (Ganges Ghats Corridor)",
            "name_hi": "वीआईपी रोड (गंगा घाट कॉरिडोर)",
            "highway": "primary",
            "maxspeed_kph": 45,
            "lanes": 4,
            "is_flood_prone_historical": True,
            "geometry": LineString([(80.32, 26.52), (80.35, 26.47)]),
        },
        # 5. Cantonment & South Eastern Links
        {
            "segment_id": "seg_cantt_01",
            "u": "Civil_Lines",
            "v": "Kanpur_Central",
            "name": "Station Approach Road",
            "name_hi": "स्टेशन अप्रोच रोड",
            "highway": "primary",
            "maxspeed_kph": 40,
            "lanes": 4,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.35, 26.47), (80.35, 26.45)]),
        },
        {
            "segment_id": "seg_cantt_02",
            "u": "Kanpur_Central",
            "v": "Kanpur_Cantonment",
            "name": "Cantonment High-Ridge Boulevard",
            "name_hi": "छावनी हाई-रिज बुलेवार्ड",
            "highway": "primary",
            "maxspeed_kph": 50,
            "lanes": 4,
            "is_flood_prone_historical": False,  # Well drained British-era cantonment
            "geometry": LineString([(80.35, 26.45), (80.38, 26.44)]),
        },
        {
            "segment_id": "seg_jajmau_01",
            "u": "Kanpur_Cantonment",
            "v": "Jajmau_Bridge",
            "name": "GT Road East (Jajmau Bypass)",
            "name_hi": "जीटी रोड ईस्ट (जाजमऊ बाईपास)",
            "highway": "trunk",
            "maxspeed_kph": 60,
            "lanes": 6,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.38, 26.44), (80.42, 26.43)]),
        },
        # 6. Industrial and Western Corridors
        {
            "segment_id": "seg_fazalganj_01",
            "u": "Rawatpur",
            "v": "Fazalganj",
            "name": "Fazalganj Main Industrial Arterial",
            "name_hi": "फजलगंज मुख्य औद्योगिक मार्ग",
            "highway": "primary",
            "maxspeed_kph": 40,
            "lanes": 4,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.29, 26.49), (80.30, 26.46)]),
        },
        {
            "segment_id": "seg_fazalganj_02",
            "u": "Fazalganj",
            "v": "Govind_Nagar",
            "name": "Fazalganj - Govind Nagar Link",
            "name_hi": "फजलगंज - गोविन्द नगर लिंक",
            "highway": "secondary",
            "maxspeed_kph": 35,
            "lanes": 2,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.30, 26.46), (80.29, 26.44)]),
        },
        {
            "segment_id": "seg_sisamau_drain",
            "u": "Fazalganj",
            "v": "Civil_Lines",
            "name": "Sisamau Drain Lowland Road",
            "name_hi": "सीसामऊ नाला निचला मार्ग",
            "highway": "tertiary",
            "maxspeed_kph": 30,
            "lanes": 2,
            "is_flood_prone_historical": True,  # Lowland drain corridor prone to overflowing
            "geometry": LineString([(80.30, 26.46), (80.35, 26.47)]),
        },
        # 7. South Peripheral Bypass
        {
            "segment_id": "seg_barra_bypass",
            "u": "Govind_Nagar",
            "v": "Barra_Bypass",
            "name": "Barra Outer Ring Link",
            "name_hi": "बर्रा आउटर रिंग लिंक",
            "highway": "primary",
            "maxspeed_kph": 50,
            "lanes": 4,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.29, 26.44), (80.28, 26.41)]),
        },
        {
            "segment_id": "seg_barra_kidwai",
            "u": "Barra_Bypass",
            "v": "Kidwai_Nagar",
            "name": "Barra - Kidwai Nagar Connector",
            "name_hi": "बर्रा - किदवई नगर कनेक्टर",
            "highway": "secondary",
            "maxspeed_kph": 45,
            "lanes": 2,
            "is_flood_prone_historical": False,
            "geometry": LineString([(80.28, 26.41), (80.34, 26.42)]),
        },
    ]

    gdf = gpd.GeoDataFrame(roads, crs=pipeline_config.WGS84_CRS)

    # Calculate metric length in EPSG:32644 (UTM 44N)
    gdf_utm = gdf.to_crs(pipeline_config.TARGET_CRS)
    gdf["length_m"] = gdf_utm.geometry.length.round(1)
    gdf["free_flow_travel_time_sec"] = (
        gdf["length_m"] / (gdf["maxspeed_kph"] * (1000.0 / 3600.0))
    ).round(1)

    return gdf


def export_osm_datasets() -> tuple[Path, Path, Path]:
    """Save roads, shelters, and waterways to GeoJSON."""
    roads_path = pipeline_config.ROADS_PATH
    shelters_path = pipeline_config.SHELTERS_PATH
    waterways_path = pipeline_config.WATERWAYS_PATH

    for p in (roads_path, shelters_path, waterways_path):
        p.parent.mkdir(parents=True, exist_ok=True)

    roads_gdf = get_kanpur_road_network()
    shelters_gdf = get_kanpur_shelters()
    waterways_gdf = get_kanpur_waterways()

    roads_gdf.to_file(roads_path, driver="GeoJSON")
    shelters_gdf.to_file(shelters_path, driver="GeoJSON")
    waterways_gdf.to_file(waterways_path, driver="GeoJSON")

    return roads_path, shelters_path, waterways_path


if __name__ == "__main__":
    r, s, w = export_osm_datasets()
    print(f"Exported roads to {r}")
    print(f"Exported shelters to {s}")
    print(f"Exported waterways to {w}")
