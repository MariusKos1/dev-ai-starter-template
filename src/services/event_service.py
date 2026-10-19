
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

API_BASE = "https://api.hel.fi/linkedevents/v1"
EVENTS_URL = f"{API_BASE}/event/"
KEYWORDS_URL = f"{API_BASE}/keyword/"

HELSINKI_TZ = ZoneInfo("Europe/Helsinki")
REQUEST_TIMEOUT = 60
PAGE_SIZE = 100
MAX_PAGES = 20

TOPIC_KEYWORD_TERMS = {
    "music": ["musiikki", "konsertti", "music", "concert"],
    "theatre": ["teatteri", "theatre", "theater"],
    "art": ["taide", "näyttely", "art exhibition", "exhibition"],
    "family": ["perhe", "lapset", "family", "children"],
    "sports": ["urheilu", "sports", "jalkapallo"],
    "food": ["ruoka", "ruokatapahtuma", "food festival"],
}


def _localized_value(value):
    """Get a readable value from a multilingual API field."""
    if isinstance(value, str):
        return value.strip()

    if isinstance(value, dict):
        for language in ("en", "fi", "sv"):
            text = value.get(language)
            if isinstance(text, str) and text.strip():
                return text.strip()

        for text in value.values():
            if isinstance(text, str) and text.strip():
                return text.strip()

    return ""


def _parse_datetime(value):
    """Parse an API datetime and convert it to Helsinki time."""
    if not value or not isinstance(value, str):
        return None

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=HELSINKI_TZ)

        return parsed.astimezone(HELSINKI_TZ)

    except (ValueError, TypeError):
        return None


def _get_date_range(target_date=None, days=7):
    """Return a Helsinki-local datetime range."""
    if target_date:
        start = datetime.combine(
            target_date, datetime.min.time(), tzinfo=HELSINKI_TZ
        )
        end = start + timedelta(days=1)
        return start, end

    start = datetime.now(HELSINKI_TZ)
    end = start + timedelta(days=days)
    return start, end


def _is_valid_url(url):
    """Accept only absolute HTTP or HTTPS URLs with a hostname."""
    if not isinstance(url, str) or not url.strip():
        return False

    try:
        parsed = urlparse(url.strip())
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )
    except ValueError:
        return False


def _event_url(raw_event):
    """Find a valid event information URL, including offer URLs."""
    candidates = [
        raw_event.get("info_url"),
    ]

    offers = raw_event.get("offers") or []
    for offer in offers:
        if isinstance(offer, dict):
            candidates.append(offer.get("info_url"))

    for candidate in candidates:
        url = _localized_value(candidate)
        if _is_valid_url(url):
            return url

    return ""


def _normalize_event(raw_event):
    """Normalize an event, rejecting records without a valid information URL."""
    name = _localized_value(raw_event.get("name"))
    start_time = _parse_datetime(raw_event.get("start_time"))
    url = _event_url(raw_event)

    # Do not return events without all required fields.
    if not name or not start_time or not url:
        return None

    return {
        "id": raw_event.get("id") or raw_event.get("@id") or name,
        "name": name,
        "start_time": start_time,
        "url": url,
    }


def _fetch_pages(url, params=None):
    """Fetch API results across multiple pages."""
    all_results = []
    next_url = url
    first_request = True

    for _ in range(MAX_PAGES):
        try:
            response = requests.get(
                next_url,
                params=params if first_request else None,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

        except requests.RequestException as error:
            print(f"[EVENT API] Request failed: {error}")
            break
        except ValueError as error:
            print(f"[EVENT API] Invalid JSON response: {error}")
            break

        first_request = False

        if isinstance(data, list):
            all_results.extend(data)
            break

        results = data.get("data", [])
        if not isinstance(results, list):
            break

        all_results.extend(results)

        meta = data.get("meta", {})
        next_url = meta.get("next")

        if not next_url:
            break

    print(f"[EVENT API] Raw records retrieved: {len(all_results)}")
    return all_results


def _deduplicate_events(raw_events, start, end, limit=None):
    """Filter by date, require links, deduplicate, and sort events."""
    events = []
    seen = set()

    for raw_event in raw_events:
        event = _normalize_event(raw_event)

        # This also filters out events without valid links.
        if event is None:
            continue

        event_start = event["start_time"]

        if not (start <= event_start < end):
            continue

        unique_key = (str(event["id"]), event_start.isoformat())

        if unique_key in seen:
            continue

        seen.add(unique_key)
        events.append(event)

    events.sort(key=lambda event: event["start_time"])

    print(
        f"[EVENT API] Events with valid links in date range: "
        f"{len(events)}"
    )

    if limit is not None:
        events = events[:limit]

    return events


def get_upcoming_events(limit=10, target_date=None, days=7):
    """Get upcoming events that have valid information links."""
    start, end = _get_date_range(target_date, days)

    print(f"[EVENT API] Date range: {start} to {end}")

    params = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "sort": "start_time",
        "page_size": PAGE_SIZE,
    }

    raw_events = _fetch_pages(EVENTS_URL, params)

    return _deduplicate_events(
        raw_events,
        start,
        end,
        limit=limit,
    )


def find_keyword_ids(search_term):
    """Find Linked Events keyword IDs matching a search term."""
    try:
        response = requests.get(
            KEYWORDS_URL,
            params={"text": search_term, "page_size": PAGE_SIZE},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as error:
        print(f"[EVENT API] Keyword search failed: {error}")
        return []

    records = data.get("data", []) if isinstance(data, dict) else []

    keyword_ids = [
        str(record["id"])
        for record in records
        if isinstance(record, dict) and record.get("id") is not None
    ]

    print(
        f"[EVENT API] Keywords for {search_term!r}: "
        f"{len(keyword_ids)}"
    )

    return keyword_ids


def search_events_by_topic(
    topic, limit=10, target_date=None, days=7
):
    """Find events for a topic, requiring valid information links."""
    terms = TOPIC_KEYWORD_TERMS.get(topic)

    if not terms:
        print(f"[EVENT API] Unknown topic: {topic}")
        return []

    keyword_ids = set()

    for term in terms:
        keyword_ids.update(find_keyword_ids(term))

    if not keyword_ids:
        print(f"[EVENT API] No keyword IDs found for {topic}")
        return []

    start, end = _get_date_range(target_date, days)

    params = {
        "keyword": ",".join(sorted(keyword_ids)),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "sort": "start_time",
        "page_size": PAGE_SIZE,
    }

    print(
        f"[EVENT API] Searching topic {topic!r}, "
        f"date range {start} to {end}"
    )

    raw_events = _fetch_pages(EVENTS_URL, params)

    return _deduplicate_events(
        raw_events,
        start,
        end,
        limit=limit,
    )
