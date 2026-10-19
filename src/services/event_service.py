
import requests
from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo

EVENTS_URL = "https://api.hel.fi/linkedevents/v1/event/"
HELSINKI_TZ = ZoneInfo("Europe/Helsinki")


def get_upcoming_events(
    limit: int = 10,
    target_date: date | str | None = None,
) -> list[dict]:
    """
    Retrieve upcoming Helsinki events from the Linked Events API.

    Args:
        limit: Maximum number of events to return.
        target_date: Optional Helsinki date, as a date object
                     or YYYY-MM-DD string.

    Returns:
        A list of unique event dictionaries.
    """
    if limit <= 0:
        return []

    now = datetime.now(HELSINKI_TZ)

    if isinstance(target_date, str):
        target_date = date.fromisoformat(target_date)

    if target_date is not None:
        local_start = datetime.combine(
            target_date,
            time.min,
            tzinfo=HELSINKI_TZ,
        )
        local_end = local_start + timedelta(days=1)
    else:
        local_start = now
        local_end = now + timedelta(days=3)

    params = {
        "start": local_start.isoformat(),
        "end": local_end.isoformat(),
        "sort": "-start_time",
        "page_size": 100,
    }

    found_events = []
    seen_ids = set()
    next_url = EVENTS_URL
    first_request = True

    try:
        while next_url and len(found_events) < limit:
            response = requests.get(
                next_url,
                params=params if first_request else None,
                timeout=20,
            )
            response.raise_for_status()
            data = response.json()

            print(
                "[DEBUG] API URL:",
                response.url,
                flush=True,
            )
            print(
                "[DEBUG] API result count:",
                len(data.get("data", [])),
                flush=True,
            )

            for item in data.get("data", []):
                event_id = item.get("id")

                # Skip duplicate records.
                if event_id is not None and event_id in seen_ids:
                    continue

                raw_start = item.get("start_time")
                if not raw_start:
                    continue

                try:
                    start_time = datetime.fromisoformat(
                        raw_start.replace("Z", "+00:00")
                    )

                    if start_time.tzinfo is None:
                        start_time = start_time.replace(
                            tzinfo=timezone.utc
                        )

                    start_time = start_time.astimezone(HELSINKI_TZ)

                except (ValueError, TypeError, AttributeError):
                    continue

                # Skip malformed years, past events, and events
                # outside the requested Helsinki date range.
                if start_time.year < now.year:
                    continue

                if target_date is not None:
                    if start_time.date() != target_date:
                        continue
                elif not (now <= start_time < local_end):
                    continue

                name_data = item.get("name") or {}

                if isinstance(name_data, dict):
                    name = (
                        name_data.get("en")
                        or name_data.get("fi")
                        or name_data.get("sv")
                        or next(
                            (
                                value
                                for value in name_data.values()
                                if isinstance(value, str) and value.strip()
                            ),
                            "",
                        )
                    )
                else:
                    name = str(name_data)

                name = name.strip()
                if not name or name == "Unnamed event":
                    continue

                # Use only a real URL supplied by the API.
                url_data = item.get("info_url") or {}

                if isinstance(url_data, dict):
                    url = (
                        url_data.get("en")
                        or url_data.get("fi")
                        or url_data.get("sv")
                        or ""
                    )
                else:
                    url = str(url_data)

                url = url.strip()

                if not url.startswith(("https://", "http://")):
                    url = ""

                # Mark an ID as seen only after it passes validation.
                if event_id is not None:
                    seen_ids.add(event_id)

                found_events.append({
                    "id": event_id,
                    "name": name,
                    "start_time": start_time.isoformat(),
                    "url": url,
                })

                if len(found_events) >= limit:
                    break

            next_url = data.get("meta", {}).get("next")
            first_request = False

    except requests.RequestException as error:
        print(
            f"[ERROR] Linked Events API request failed: {error}",
            flush=True,
        )
        raise

    found_events.sort(key=lambda event: event["start_time"])

    print(
        f"[INFO] Returning {len(found_events)} unique upcoming events.",
        flush=True,
    )

    return found_events
