"""
Optional project capability: Tools & External API Integration.

Implement this module only if this capability is relevant to your application's
user problem. Remove the file if the capability is not used.

Conceptual Overview:
-------------------
Tools allow the AI application to perform operations beyond text generation,
such as fetching live data from external APIs, performing calculations, or
executing internal application functions.

Key concepts when implementing tools:
1. Tool Definition: Defining function schemas (names, descriptions, parameters)
   that describe what each tool does.
2. Model Tool Calling: Providing tool schemas to the model so it can request tool execution
   when needed.
3. Execution & Response: Parsing tool call requests, executing the corresponding
   Python function or API call, and passing the results back to the model or user.

Note:
-----
Tools should be deterministic, safe, and scoped to the user problem.
"""

# Implement custom tool functions and schema definitions below if selected.

# Defines the tool schema for searching upcoming events in Helsinki.
EVENT_TOOL = {
    "type": "function",
    "function": {
        "name": "get_upcoming_events",
        "description": "Get upcoming events in Helsinki.",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of days ahead to search for events."
                }
            },
            "required": ["days"]
        }
    }
}

def get_upcoming_events(days: int):
    """
    Returns example upcoming events in Helsinki.
    """
    events = [
        {
            "name": "Helsinki Tech Meetup",
            "location": "Helsinki",
            "days_from_now": 2,
        },
        {
            "name": "AI Developer Workshop",
            "location": "Helsinki",
            "days_from_now": 5,
        },
        {
            "name": "Startup Networking Evening",
            "location": "Helsinki",
            "days_from_now": 10,
        },
    ]

    return [
        event
        for event in events
        if event["days_from_now"] <= days
    ]