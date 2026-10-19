
from ollama import Client, ResponseError

MODEL_ID = "qwen3:1.7b"
OLLAMA_HOST = "http://localhost:11434"

client = Client(
    host=OLLAMA_HOST,
    timeout=300,
)


class ModelClientError(Exception):
    """A controlled error from the Ollama client."""


def ask_ollama(prompt: str, system_message: str) -> str:
    """Generate a response using the local Ollama model."""
    try:
        response = client.chat(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
        )

        answer = response["message"]["content"].strip()

        if not answer:
            raise ModelClientError(
                "The AI model returned an empty response."
            )

        return answer

    except ModelClientError:
        raise

    except ResponseError as error:
        raise ModelClientError(
            f"Ollama response error: {error}"
        ) from error

    except Exception as error:
        raise ModelClientError(
            "Could not communicate with Ollama. "
            "Check that Ollama is running and try again."
        ) from error
