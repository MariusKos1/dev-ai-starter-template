
from ollama import Client, ResponseError


MODEL_ID = "qwen3:8b"
OLLAMA_HOST = "http://localhost:11434"

model_client = Client(
    host=OLLAMA_HOST,
    timeout=200.0
)


class ModelClientError(Exception):
    """A controlled error from the Ollama client."""


def ask_ollama(prompt: str) -> str:
    """Check the model and generate a chat response."""

    try:
        installed_models = {
            item.model
            for item in model_client.list().models
        }

        if MODEL_ID not in installed_models:
            raise ModelClientError(
                f"Model {MODEL_ID!r} is not installed. "
                f"Run: ollama pull {MODEL_ID}"
            )

        response = model_client.chat(
            model=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            think=False
        )

        answer = response.message.content

        if not answer or not answer.strip():
            raise ModelClientError(
                "The AI model returned an empty response."
            )

        return answer.strip()

    except ModelClientError:
        raise

    except ResponseError as exc:
        raise ModelClientError(
            f"Ollama could not generate a response: {exc.error}"
        ) from exc

    except Exception as exc:
        # Covers connection errors, timeouts, and other
        # unexpected errors from the client library.
        raise ModelClientError(
            "Could not communicate with Ollama. "
            "Check that Ollama is running and try again."
        ) from exc
