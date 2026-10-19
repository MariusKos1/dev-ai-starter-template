
import os
import re
import time
import traceback
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ollama import Client, ResponseError
from src.services.event_service import get_upcoming_events


print(
    f"[DEBUG] ai_service.py loaded from: {os.path.abspath(__file__)}",
    flush=True,
)

MODEL_ID = "qwen3:1.7b"
OLLAMA_HOST = "http://localhost:11434"
HELSINKI_TZ = ZoneInfo("Europe/Helsinki")

model_client = Client(host=OLLAMA_HOST, timeout=300.0)


SYSTEM_MESSAGE = (
    "You are a Helsinki tourist assistant. "
    "Help users discover restaurants, attractions, and events "
    "in Helsinki. Be friendly, concise, and answer in the "
    "language used by the user. "
    "When event data is provided, use it as the source of truth "
    "for event names, times, and URLs. "
    "Do not invent event locations, restaurant listings, "
    "opening hours, prices, or other unverified details. "
    "If the available information is insufficient, explain this "
    "clearly. Present event times in Helsinki local time. "
    "Keep answers concise, using short bullet points when appropriate. "
    "Finish each bullet point before starting another. "
    "Do not include lengthy introductions."
)


def is_event_question(question: str) -> bool:
    """Check whether the user is asking about events or activities."""

    question_lower = question.lower()

    event_keywords = re.compile(
        r"\b("
        r"event|events|concert|concerts|gig|gigs|"
        r"festival|festivals|exhibition|exhibitions|"
        r"performance|performances|theatre|theater|"
        r"play|plays|what's on|happening|"
        r"tapahtuma|tapahtumat|konsertti|konsertit|"
        r"näyttely|näyttelyt|esitys|esitykset|"
        r"evenemang|föreställning|utställning"
        r")\b"
    )

    time_keywords = re.compile(
        r"\b("
        r"today|tonight|tomorrow|tommorow|this weekend|"
        r"upcoming|next weekend|"
        r"tänään|huomenna|viikonloppuna|"
        r"idag|imorgon|i helgen"
        r")\b"
    )

    activity_phrases = (
        "things to do",
        "activities in helsinki",
        "what can i do",
        "what is happening",
        "what's happening",
        "what to do in helsinki",
    )

    return (
        bool(event_keywords.search(question_lower))
        or bool(time_keywords.search(question_lower))
        or any(
            phrase in question_lower
            for phrase in activity_phrases
        )
    )


def is_simple_event_list_question(question: str) -> bool:
    """
    Identify event-list requests that can be answered directly
    from API data without using the language model.
    """

    question_lower = question.lower()

    special_intent = re.compile(
        r"\b("
        r"best|recommend|recommendation|recommended|"
        r"good for|suitable for|"
        r"kid|kids|child|children|family|families|"
        r"free|cheap|budget|indoor|outdoor|"
        r"near me|nearby|closest|"
        r"compare|difference|explain|"
        r"why|how|which|where"
        r")\b"
    )

    if special_intent.search(question_lower):
        return False

    listing_intent = re.compile(
        r"\b("
        r"list|show|give me|find|"
        r"upcoming|event|events|concert|concerts|"
        r"festival|festivals|exhibition|exhibitions|"
        r"what's on|what is on|what is happening|"
        r"what's happening|"
        r"tapahtuma|tapahtumat|konsertti|konsertit|"
        r"näyttely|näyttelyt"
        r")\b"
    )

    return bool(listing_intent.search(question_lower))


def get_requested_event_count(question: str) -> int:
    """Extract a requested event count, defaulting to five."""

    patterns = (
        r"\b(\d+)\s+events?\b",
        r"\b(\d+)\s+concerts?\b",
        r"\b(\d+)\s+festivals?\b",
        r"\b(\d+)\s+exhibitions?\b",
    )

    for pattern in patterns:
        match = re.search(pattern, question.lower())

        if match:
            return max(1, min(int(match.group(1)), 30))

    return 5


def format_event_list(
    events: list[dict],
    title: str,
) -> str:
    """Format event details directly from the API."""

    if not events:
        return (
            f"I couldn't find any matching events for {title} "
            "in the retrieved event data."
        )

    lines = [f"Here are {len(events)} events for {title}:"]

    for event in events:
        name = event.get("name") or "Unnamed event"
        url = (event.get("url") or "").strip()
        raw_start_time = event.get("start_time", "")

        try:
            start_time = datetime.fromisoformat(
                raw_start_time.replace("Z", "+00:00")
            )

            if start_time.tzinfo is None:
                start_time = start_time.replace(
                    tzinfo=HELSINKI_TZ
                )

            start_time = start_time.astimezone(HELSINKI_TZ)

            formatted_time = start_time.strftime(
                "%a %d %b, %H:%M"
            )

        except (ValueError, TypeError, AttributeError):
            formatted_time = "Time unavailable"

        line = f"- **{name}** — {formatted_time}"

        # Only show links provided by the API.
        if url.startswith(("https://", "http://")):
            line += f" — [Event details]({url})"

        lines.append(line)

    return "\n".join(lines)


def filter_events_for_date(
    events: list[dict],
    target_date,
) -> list[dict]:
    """Keep events whose start date matches the target date."""

    matching_events = []

    for event in events:
        try:
            raw_start_time = event["start_time"]

            start_time = datetime.fromisoformat(
                raw_start_time.replace("Z", "+00:00")
            )

            if start_time.tzinfo is None:
                start_time = start_time.replace(
                    tzinfo=HELSINKI_TZ
                )

            start_time = start_time.astimezone(HELSINKI_TZ)

            if start_time.date() == target_date:
                matching_events.append(event)

        except (
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
        ):
            continue

    matching_events.sort(
        key=lambda event: event.get("start_time", "")
    )

    return matching_events


def generate_response(question: str) -> str:
    """Generate a response using event data and Ollama as needed."""

    total_start = time.perf_counter()
    cleaned_question = (question or "").strip()

    if not cleaned_question:
        return "Please enter a question."

    context = ""
    stage = "event retrieval"

    try:
        if is_event_question(cleaned_question):
            question_lower = cleaned_question.lower()

            requested_count = get_requested_event_count(
                cleaned_question
            )

            simple_list_request = is_simple_event_list_question(
                cleaned_question
            )

            asks_for_tomorrow = (
                "tomorrow" in question_lower
                or "tommorow" in question_lower
                or "huomenna" in question_lower
                or "imorgon" in question_lower
            )

            asks_for_today = (
                "today" in question_lower
                or "tonight" in question_lower
                or "tänään" in question_lower
                or "idag" in question_lower
            )

            # Determine whether the API should search a specific date.
            today = datetime.now(HELSINKI_TZ).date()
            target_date = None

            if asks_for_today:
                target_date = today
            elif asks_for_tomorrow:
                target_date = today + timedelta(days=1)

            event_start = time.perf_counter()

            # Request today's or tomorrow's events directly from
            # the API, rather than filtering a general event list.
            if target_date is not None:
                events = get_upcoming_events(
                    limit=30,
                    target_date=target_date,
                )
            else:
                events = get_upcoming_events(limit=30)

            event_elapsed = time.perf_counter() - event_start

            print(
                f"[TIMING] Event retrieval: {event_elapsed:.2f}s",
                flush=True,
            )
            print(
                f"[INFO] Retrieved {len(events)} events.",
                flush=True,
            )

            # Answer simple requests directly from API data.
            if simple_list_request:
                selected_events = events[:requested_count]

                if target_date is not None:
                    title = target_date.strftime("%d %B %Y")
                else:
                    title = "upcoming events in Helsinki"

                answer = format_event_list(
                    selected_events,
                    title,
                )

                if (
                    len(selected_events) < requested_count
                    and selected_events
                ):
                    answer += (
                        f"\n\nI found only {len(selected_events)} "
                        "matching events in the retrieved data."
                    )

                total_elapsed = time.perf_counter() - total_start

                print(
                    "[INFO] Answered directly from event API data.",
                    flush=True,
                )
                print(
                    f"[TIMING] Total response time: "
                    f"{total_elapsed:.2f}s",
                    flush=True,
                )

                return answer

            # Use the language model for questions requiring
            # recommendations, explanations, or filtering.
            if events:
                context = "Retrieved events:\n" + "\n".join(
                    f"- {event.get('name', 'Unnamed event')} | "
                    f"{event.get('start_time', 'Time unavailable')} | "
                    f"{event.get('url', '')}"
                    for event in events
                )
            else:
                context = (
                    "No events were found in the requested search "
                    "window. Do not invent event listings."
                )

        # Generate AI answers for questions that need reasoning
        # and for questions unrelated to event listings.
        user_message = cleaned_question

        if context:
            user_message += (
                "\n\nRetrieved event information:\n"
                + context
                + "\n\nUse only the supplied event information. "
                "Preserve event names, times, and URLs exactly. "
                "Do not invent additional events or details."
            )

        stage = "Ollama response generation"
        ai_start = time.perf_counter()

        print("[DEBUG] Model call reached.", flush=True)
        print(f"[DEBUG] Model: {MODEL_ID}", flush=True)
        print(
            f"[DEBUG] Prompt length: {len(user_message)} characters",
            flush=True,
        )

        response = model_client.chat(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_MESSAGE,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            think=False,
            options={"num_predict": 512},
            stream=False,
        )

        ai_elapsed = time.perf_counter() - ai_start
        total_elapsed = time.perf_counter() - total_start

        print(
            f"[TIMING] Ollama generation: {ai_elapsed:.2f}s",
            flush=True,
        )
        print(
            f"[TIMING] Total response time: {total_elapsed:.2f}s",
            flush=True,
        )

        answer = response.message.content

        if not answer or not answer.strip():
            return (
                "The AI returned an empty response. "
                "Please try again."
            )

        return answer.strip()

    except ResponseError as error:
        print(
            f"[ERROR] Ollama error during {stage}: {error!r}",
            flush=True,
        )
        traceback.print_exc()

        return (
            "Ollama could not process your request. "
            "Check that the model is available and try again."
        )

    except Exception as error:
        print(
            f"[ERROR] Failure during {stage}: {error!r}",
            flush=True,
        )
        traceback.print_exc()

        return (
            f"An error occurred during {stage}: "
            f"{type(error).__name__}: {error}"
        )
