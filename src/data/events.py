import requests
from datetime import datetime, timedelta

def fetch_events():
    today = datetime.now().date()
    end_date = today + timedelta(days=3)

    url = url = (
    f"https://api.hel.fi/linkedevents/v1/event/"
    f"?start={today}&end={end_date}"
)

    data = requests.get(url).json()

    results = []
    for event in data["data"]:
        results.append({
            "name": event["name"].get("fi"),
            "date": event["start_time"],
            "location": event["location"]["name"]["fi"]
        })

    return results

#Pauliina: Real Open api does not work, so I have created a mock data for events, just  testing purposes. 