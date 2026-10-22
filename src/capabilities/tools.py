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

### Custom API Tools

The application implements custom Python functions in src/services/event_service.py to retrieve event information from the Helsinki Linked Events API.
1. get_upcoming_events
Purpose: Retrieves upcoming events in Helsinki within a specified date range.
Inputs:
- limit (integer): Maximum number of events returned.
- target_date (date or None): Optional target date.
- days (integer): Number of days to search when no target date is specified.
Output: A list of normalized event dictionaries containing the event ID, name, start time, and information URL.
2. search_events_by_topic
Purpose: Retrieves events associated with a supported topic, such as music, theatre, art, family activities, sports, or food.
Inputs:
- topic (string): The topic to search for.
- limit (integer): Maximum number of events returned.
- target_date (date or None): Optional target date.
- days (integer): Search-window length in days.
Output: A list of matching event dictionaries, filtered by date and valid information links.
3. find_keyword_ids
Purpose: Searches the Linked Events keyword endpoint for keywords matching a search term.
Input: search_term (string).
Output: A list of keyword IDs used to filter event searches.
API and Data Validation
The functions use HTTP GET requests to access the Helsinki Linked Events API. Retrieved events are normalized and filtered to remove invalid records, events outside the requested date range, and duplicates. Events without valid HTTP or HTTPS information URLs are excluded.
Tool Execution
The service layer in src/services/ai_service.py determines whether a question concerns events and calls the appropriate event-service function. The application selects and executes these functions using predefined Python logic; the language model does not independently select or execute tools.



