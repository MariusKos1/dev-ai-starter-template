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
"""Resturant search tool
1. Tool defination: the purpose of this tool is to retrieve restaurant information in Helsinki usin Geoapify places API. 
The tool is implemented as the following funtion: 
search_restaurants(cuisine="", limit=10)

Parameters:
cuisine: Preferred cuisine type (e.g., italian, japanese, indian)
limit: Maximum number of restaurants to return

Returned Data
The function returns a list of restaurants containing the following information:
{
    "name": "Restaurant Name",
    "address": "Restaurant Address",
    "cuisine": "Cuisine Type",
    "website": "Website URL",
    "latitude": 60.17,
    "longitude": 24.94
} 

2. Model Tool Calling

The AI service identifies restaurant-related user questions through intent classification.
Examples of supported questions:
   Show me Italian restaurants
   Show me sushi restaurants
   Find restaurants in Helsinki
   
The ai_service.py file uses the following functions:
   is_restaurant_question()
   get_restaurant_topic()
   
When a restaurant-related query is detected, the AI service calls the restaurant search tool:
   search_restaurants(
      cuisine=cuisine,
      limit=count
)
The cuisine type is extracted from the user's request and passed to the API search.

3. Execution & Response

When the tool is executed, it performs the following steps:

1. API Key Loading

The API key is loaded from the .env file.
   api_key = os.getenv("GEOAPIFY_API_KEY")

If the key is not found, the system raises an error:
   GEOAPIFY_API_KEY is missing from .env
   
This prevents invalid API requests and simplifies troubleshooting.

2. API Request

The tool sends an HTTP request to the Geoapify Places API.
   response = requests.get(
      GEOAPIFY_URL,
      params=params,
      timeout=30
)
The search is restricted to the Helsinki city center area within a 5 km radius.
   "filter": "circle:24.9405947,60.1715453,5000"

3. Result Processing

The returned restaurant data is processed, and the most relevant information is extracted:

   Name
   Address
   Cuisine type
   Website
   Coordinates

Cuisine filtering is also applied when requested:
   if cuisine and cuisine.lower() not in restaurant_cuisine.lower():
      continue

4. Response Generation

The processed restaurant data is returned to ai_service.py, which formats the results for the user.

Example response:
   Restaurants in Helsinki

   • Olivia Central Station
      Cuisine: italian
      Address: Kaivokatu 1, Helsinki 
 
 The restaurant search tool enables real-time restaurant recommendations by using the Geoapify Places API. 
 The AI service detects restaurant-related questions, performs the necessary API requests, 
 and returns restaurant recommendations based on restaurant name, address, and cuisine type. 
 This functionality extends the Helsinki Visit Assistant from event recommendations to restaurant 
 recommendations within the same application."""
