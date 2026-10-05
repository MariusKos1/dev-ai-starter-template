from email.mime import message
from typing import Optional
from xmlrpc import client

from prompt_toolkit import prompt

from prompt_toolkit import prompt
from src.models.model_client import (
    OllamaModelClient,
    ModelClientError,
    OllamaConnectionError,
    ModelNotFoundError,
)
from src.schemas.responses import UserRequest, AIResponse
from src.data.restaurants import fetch_restaurants #PAULIINALISÄYS
from src.data.events import fetch_events #PAULIINA LISÄYS



class AIService:
    """
    Application service layer responsible for validating user input,
    orchestrating model client requests, and catching exceptions gracefully.
    """

    def __init__(self, model_client: Optional[OllamaModelClient] = None):
        # Allow injecting custom/mock model_client for simple testing
        self.model_client = model_client


    def _get_client(self) -> OllamaModelClient:
        """Returns active model client, initializing default client if none provided."""
        if self.model_client is None:
            self.model_client = OllamaModelClient()
        return self.model_client

    def classify_intent(self, message: str) -> str: #PAULIINA LISÄYS
            prompt = f"""
            Classify the user query into one of the following:
         - restaurants
         - events
            - both
    
            Only answer with one word.
    
            Query: {message}
        """
            client = self._get_client()
            intent = client.generate(prompt).strip().lower()
            return intent
    from src.data.restaurants import fetch_restaurants
from src.data.events import fetch_events

def build_context(self, intent: str) -> str: #PAULIINA LISÄYS
    context = ""

    if intent in ["restaurants", "both"]:
        restaurants = fetch_restaurants()
        context += "RESTAURANTS:\n"
        for r in restaurants:
            context += f"- {r['name']} (rating {r['rating']}) at {r['address']}\n"

    if intent in ["events", "both"]:
        events = fetch_events()
        context += "\nEVENTS:\n"
        for e in events:
            context += f"- {e['name']} on {e['date']} at {e['location']}\n"

    return context


    # def process_message(self, user_message: str) -> AIResponse:
    #     """
    #     Processes a raw user message string and returns a structured AIResponse.
    #     Catches technical failures and converts them to friendly user-facing messages.
    #     """
    #     # 1. Validate empty input
    #     if not user_message or not user_message.strip():
    #         return AIResponse(
    #             content="Please enter a message before sending.",
    #             success=False,
    #             error_message="User message was empty.",
    #         )

    #     try:
    #         # 2. Schema validation
    #         request = UserRequest(message=user_message.strip())

    #         # 3. Call model client
    #         client = self._get_client()
    #         response_text = client.generate(request.message)

    #         return AIResponse(
    #             content=response_text,
    #             success=True,
    #         )

    #     except OllamaConnectionError as err:
    #         return AIResponse(
    #             content=(
    #                 "[Error] Could not connect to Ollama.\n\n"
    #                 "Please verify that Ollama is installed and running locally on your machine."
    #             ),
    #             success=False,
    #             error_message=str(err),
    #         )

    #     except ModelNotFoundError as err:
    #         return AIResponse(
    #             content=(
    #                 f"[Error] The configured AI model is unavailable in Ollama.\n\n"
    #                 f"Please verify your MODEL_NAME setting or run 'ollama run <model_name>'."
    #             ),
    #             success=False,
    #             error_message=str(err),
    #         )

    #     except ModelClientError as err:
    #         return AIResponse(
    #             content="[Error] An unexpected communication error occurred with the AI model.",
    #             success=False,
    #             error_message=str(err),
    #         )

    #     except Exception as err:
    #         return AIResponse(
    #             content="[Error] An unexpected application error occurred.",
    #             success=False,
    #             error_message=str(err),
    #         )
   
def process_message(self, user_message: str) -> AIResponse: #PAULIINA LISÄYS
    if not user_message or not user_message.strip():
        return AIResponse(
            content="Please enter a message before sending.",
            success=False,
            error_message="User message was empty.",
        )

    try:
        # 1. Intent-luokittelu
        intent = self.classify_intent(user_message)

        # 2. API-data
        context = self.build_context(intent)

        # 3. Lopullinen prompt
        final_prompt = f"""
        You are a Helsinki travel assistant.

        USER QUERY:
        {user_message}

        CONTEXT:
        {context}

        INSTRUCTIONS:
        - Recommend the best plan for the user.
        - Use only the provided context.
        - Be concise and helpful.
        """

        # 4. Mallikutsu
        client = self._get_client()
        response_text = client.generate(final_prompt)

        return AIResponse(
            content=response_text,
            success=True,
        )

    except Exception as err:
        return AIResponse(
            content="[Error] An unexpected application error occurred.",
            success=False,
            error_message=str(err),
        )




def generate_response(user_message: str, service: Optional[AIService] = None) -> str:
    """
    Main reusable service entry point used by the UI layer.
    
    Accepts user input message, passes it to the AI service, and returns
    the generated text response (or a friendly error message).
    """
    active_service = service or AIService()
    response = active_service.process_message(user_message)
    return response.content
