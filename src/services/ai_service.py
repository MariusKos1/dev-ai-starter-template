
import re
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from src.services.restaurant_service import search_restaurants
from src.services.attraction_service import search_attractions

from src.services.ollama_client import (
    ask_ollama,
    ModelClientError,
)

from src.services.event_service import (
    get_upcoming_events,
    search_events_by_topic,
)

HELSINKI_TZ = ZoneInfo("Europe/Helsinki")

SYSTEM_MESSAGE = """
You are a helpful Helsinki tourist assistant.

Answer in the same language as the user's question.
Be concise and friendly.
Use only the information provided in the context.
Never invent event names, dates, links, opening hours, or prices.
If the provided information is insufficient, say so clearly.
"""

TOPIC_LABELS = {
    "music": "Music-related events",
    "theatre": "Theatre events",
    "art": "Art and exhibition events",
    "family": "Family events",
    "sports": "Sports events",
    "food": "Food-related events",
}


def is_event_question(question):
    """Check whether the user is asking about events."""
    terms = [
        "event", "events", "concert", "concerts", "gig", "gigs",
        "festival", "festivals", "exhibition", "exhibitions",
        "performance", "performances", "what's on", "happening",
        "things to do", "activities", "music-related",
        "tapahtuma", "tapahtumat", "konsertti", "konsertit",
        "näyttely", "näyttelyt", "keikka", "keikat",
        "evenemang", "konsert", "utställning",
    ]

    lowered = question.lower()
    return any(term in lowered for term in terms)


def get_event_topic(question):
    """Identify a supported event topic, if present."""
    lowered = question.lower()

    topic_terms = {
        "music": [
            "music", "musical", "concert", "concerts",
            "gig", "gigs", "live music", "musiikki",
            "konsertti", "konsertit", "keikka", "keikat",
        ],
        "theatre": [
            "theatre", "theater", "play", "plays",
            "teatteri", "teatteriesitys",
        ],
        "art": [
            "art", "exhibition", "exhibitions",
            "gallery", "museum", "taide", "näyttely",
        ],
        "family": [
            "family", "families", "children", "kids",
            "perhe", "lapset",
        ],
        "sports": [
            "sport", "sports", "football", "basketball",
            "urheilu", "jalkapallo",
        ],
        "food": [
            "food festival", "food event", "food events",
            "ruokatapahtuma", "ruokatapahtumat",
        ],
    }

    for topic, terms in topic_terms.items():
        if any(term in lowered for term in terms):
            return topic

    return None


def get_requested_event_count(question):
    """Extract the requested event count, defaulting to 10."""
    patterns = [
        r"\b(\d{1,2})\s+(?:events?|concerts?|exhibitions?)\b",
        r"\b(?:top|first)\s+(\d{1,2})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            return max(1, min(int(match.group(1)), 30))

    return 10


def get_requested_date(question):
    """Recognize today and tomorrow in common English and Finnish."""
    lowered = question.lower()
    today = datetime.now(HELSINKI_TZ).date()

    today_terms = [
        "today", "tonight", "tänään", "tanään",
        "idag", "ikväll",
    ]
    tomorrow_terms = [
        "tomorrow", "tommorow", "huomenna", "imorgon",
    ]

    if any(term in lowered for term in tomorrow_terms):
        return today + timedelta(days=1)

    if any(term in lowered for term in today_terms):
        return today

    return None


def get_requested_days(question):
    """Determine the requested upcoming time window."""
    lowered = question.lower()

    if any(
        term in lowered
        for term in [
            "next week", "upcoming week", "coming week",
            "this week", "next 7 days", "next seven days",
            "ensi viikolla", "tulevalla viikolla",
            "den kommande veckan",
        ]
    ):
        return 7

    return 7


def get_date_label(target_date=None, days=7):
    """Create a readable date label."""
    if target_date:
        today = datetime.now(HELSINKI_TZ).date()

        if target_date == today:
            return "today"

        if target_date == today + timedelta(days=1):
            return "tomorrow"

        return target_date.strftime("%A %d %b")

    return f"the next {days} days"


def _has_valid_url(event):
    """Only accept events with absolute HTTP/HTTPS information links."""
    url = event.get("url")

    if not isinstance(url, str) or not url.strip():
        return False

    try:
        parsed = urlparse(url.strip())
        return (
            parsed.scheme in ("https", "http")
            and bool(parsed.netloc)
        )
    except ValueError:
        return False


def format_event_list(events, title):
    """Format only events that have valid clickable links."""
    events = [
        event for event in events
        if _has_valid_url(event)
    ]

    if not events:
        return (
            f"**{title}**\n\n"
            "I couldn't find matching events with valid information "
            "links. Try another date or topic."
        )

    lines = [f"**{title}**", ""]

    for event in events:
        name = event["name"]
        url = event["url"]
        start_time = event["start_time"]

        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(
                    start_time.replace("Z", "+00:00")
                )
            except ValueError:
                start_time = None

        if isinstance(start_time, datetime):
            if start_time.tzinfo is None:
                start_time = start_time.replace(
                    tzinfo=HELSINKI_TZ
                )

            start_time = start_time.astimezone(HELSINKI_TZ)
            date_text = start_time.strftime("%a %d %b, %H:%M")
        else:
            date_text = "Time unavailable"

        lines.append(f"- [{name}]({url}) — {date_text}")

    return "\n".join(lines)


def generate_response(question):
    """Route event questions to the event service and other questions to Ollama."""
    started = time.time()

    try:
        event_question = is_event_question(question)
        topic = get_event_topic(question)
        target_date = get_requested_date(question)
        days = get_requested_days(question)
        count = get_requested_event_count(question)

        # Handle event-list questions directly instead of calling Ollama.
        if event_question or topic:
            date_label = get_date_label(target_date, days)

            if topic:
                events = search_events_by_topic(
                    topic=topic,
                    limit=count,
                    target_date=target_date,
                    days=days,
                )

                title = (
                    f"{TOPIC_LABELS.get(topic, 'Events')} "
                    f"happening {date_label} in Helsinki"
                )
            else:
                events = get_upcoming_events(
                    limit=count,
                    target_date=target_date,
                    days=days,
                )

                title = (
                    f"Events happening {date_label} in Helsinki"
                )

            answer = format_event_list(events, title)

            print(
                f"[AI SERVICE] Event response completed in "
                f"{time.time() - started:.2f}s"
            )

            return answer

        
        # Handle restaurant questions using the Geoapify API.
        restaurant_keywords = [
            "restaurant", "restaurants",
            "restaurante", "restaurantes",
            "ravintola", "ravintolat",
            "where to eat", "places to eat",
        ]

        if any(word in question.lower() for word in restaurant_keywords):
            restaurants = search_restaurants(limit=10)

            if not restaurants:
                return "No restaurants were found in Helsinki."

            lines = ["### Restaurants in Helsinki\n"]

            for restaurant in restaurants:
                name = restaurant["name"]
                address = restaurant["address"]
                website = restaurant.get("website", "")

                if website:
                    lines.append(f"- **[{name}]({website})** — {address}")
                else:
                    lines.append(f"- **{name}** — {address}")

            print(
                f"[AI SERVICE] Restaurant response completed in "
                f"{time.time() - started:.2f}s"
            )

            return "\n".join(lines)


        # Handle attraction questions using Geoapify.
        attraction_keywords = [
            "attraction", "attractions",
            "sightseeing", "sights",
            "tourist places", "places to visit",
            "atracciones", "lugares turísticos",
            "nähtävyys", "nähtävyydet",
        ]

        if any(word in question.lower() for word in attraction_keywords):
            attractions = search_attractions(limit=10)

            if not attractions:
                return "No attractions were found in Helsinki."

            lines = ["### Attractions in Helsinki\n"]

            for attraction in attractions:
                name = attraction["name"]
                address = attraction["address"]
                website = attraction.get("website", "")

                if website:
                    lines.append(
                        f"- **[{name}]({website})** — {address}"
                    )
                else:
                    lines.append(
                        f"- **{name}** — {address}"
                    )

            print(
                f"[AI SERVICE] Attraction response completed "
                f"in {time.time() - started:.2f}s"
            )

            return "\n".join(lines)


        # For non-event questions, use the Ollama client service.
        answer = ask_ollama(
            prompt=question,
            system_message=SYSTEM_MESSAGE,
        )

        print(
            f"[AI SERVICE] Ollama response completed in "
            f"{time.time() - started:.2f}s"
        )

        return answer

    except ModelClientError as error:
        print(f"[AI SERVICE] Ollama error: {error}")
        return "I couldn't generate a response. Please try again."

    except Exception as error:
        print(f"[AI SERVICE] Unexpected error: {error}")
        return (
            "Something went wrong while retrieving information. "
            "Please try again."
        )
