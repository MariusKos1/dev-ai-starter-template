import requests

def fetch_restaurants():
    url = "https://open-api.myhelsinki.fi/v1/places/"
    data = requests.get(url).json()

    results = []
    for item in data["data"]:
        rating = item.get("rating", 0)
        if rating >= 4.5:
            results.append({
                "name": item["name"]["fi"],
                "address": item["location"]["address"]["street_address"],
                "rating": rating
            })

    return results
import requests

#Pauliina: Real Open api does not work, so I have created a mock data for restaurants, just testing purposes.
