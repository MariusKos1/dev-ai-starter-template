def fetch_restaurants():
    """
    Mock data for restaurants.
    Used because the real MyHelsinki API is unstable or offline.
    """
    return [
        {
            "name": "Ravintola Aito",
            "address": "Museokatu 29, Helsinki",
            "rating": 4.7
        },
        {
            "name": "Ravintola Nokka",
            "address": "Kanavaranta 7, Helsinki",
            "rating": 4.6
        },
        {
            "name": "Ravintola Olo",
            "address": "Pohjoisesplanadi 5, Helsinki",
            "rating": 4.8
        }
    ]
