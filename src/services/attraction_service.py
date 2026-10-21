
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"


def search_attractions(limit=10):
    """Find real tourist attractions in Helsinki."""

    api_key = os.getenv("GEOAPIFY_API_KEY")

    if not api_key:
        raise ValueError("GEOAPIFY_API_KEY is missing from .env")

    params = {
        "categories": "tourism.attraction,tourism.sights",
        "filter": "circle:24.9405947,60.1715453,5000",
        "bias": "proximity:24.9405947,60.1715453",
        "limit": min(max(limit, 1), 20),
        "apiKey": api_key,
    }

    response = requests.get(
        GEOAPIFY_URL,
        params=params,
        timeout=30
    )
    response.raise_for_status()

    attractions = []

    for feature in response.json().get("features", []):
        properties = feature.get("properties", {})
        name = properties.get("name")

        if not name:
            continue

        raw = properties.get("datasource", {}).get("raw", {})

        attractions.append({
            "name": name,
            "address": properties.get(
                "formatted", "Address unavailable"
            ),
            "website": properties.get("website")
                       or raw.get("website", ""),
            "latitude": properties.get("lat"),
            "longitude": properties.get("lon"),
        })

    return attractions
