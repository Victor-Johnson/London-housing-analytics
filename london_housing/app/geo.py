import json
import os

import requests
import streamlit as st

# ONS Local Authority Districts boundary GeoJSON (simplified, public domain)
# BGC = Boundaries Generalised Clipped — lower resolution, faster to load
GEOJSON_URL = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "Local_Authority_Districts_May_2024_Boundaries_UK_BGC/FeatureServer/0/query"
    "?where=1%3D1&outFields=LAD24NM&f=geojson&returnGeometry=true"
)
GEOJSON_CACHE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "districts.geojson"
)


@st.cache_data(ttl=86400 * 30)
def load_geojson():
    if os.path.exists(GEOJSON_CACHE):
        with open(GEOJSON_CACHE) as f:
            return json.load(f)
    try:
        resp = requests.get(GEOJSON_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        os.makedirs(os.path.dirname(GEOJSON_CACHE), exist_ok=True)
        with open(GEOJSON_CACHE, "w") as f:
            json.dump(data, f)
        return data
    except Exception:
        return None


def with_uppercase_district_key(geojson):
    """Adds an uppercased district-name property for case-insensitive joins against district data."""
    for feature in geojson["features"]:
        name = feature["properties"].get("LAD24NM", "")
        feature["properties"]["LAD24NM_upper"] = name.upper()
    return geojson
