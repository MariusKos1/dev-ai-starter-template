def fetch_events():
    """
    Mock data for events.
    Used because the real Linked Events API is unstable or offline.
    """
    return [
        {
            "name": "Helsinki Jazz Night",
            "date": "2026-10-06",
            "location": "Savoy-teatteri"
        },
        {
            "name": "Design Week Pop-up",
            "date": "2026-10-07",
            "location": "Keskusta"
        },
        {
            "name": "Outdoor Yoga",
            "date": "2026-10-08",
            "location": "Kaivopuisto"
        }
    ]
