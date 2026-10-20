
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"


def search_restaurants(cuisine="", limit=10):
    """Search for real restaurants in Helsinki using Geoapify."""

    api_key = os.getenv("GEOAPIFY_API_KEY")

    if not api_key:
        raise ValueError("GEOAPIFY_API_KEY is missing from .env")

    params = {
        "categories": "catering.restaurant",
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

    restaurants = []

    for feature in response.json().get("features", []):
        properties = feature.get("properties", {})
        name = properties.get("name")

        if not name:
            continue

        categories = properties.get("categories", [])
        details = properties.get("datasource", {}).get("raw", {})
        restaurant_cuisine = details.get("cuisine", "")

        if cuisine and cuisine.lower() not in restaurant_cuisine.lower():
            continue

        restaurants.append({
            "name": name,
            "address": properties.get("formatted", "Address unavailable"),
            "cuisine": restaurant_cuisine,
            "website": properties.get("website") or details.get("website", ""),
            "latitude": properties.get("lat"),
            "longitude": properties.get("lon"),
        })

    return restaurants
