# Visiting plan assistant for restaraunts and upcoming events for the city of Helsinki

Starter template for the **Development of AI Applications** course final group project.

Link to the video of the application: https://www.youtube.com/watch?v=uChXM7iUip0

## Team members

- Marius Koskinen (marius.koskinen@student.hamk.fi)
- Pauliina Touruvirta (anna-pauliina.touruvirta@student.hamk.fi)
- Aki Sartolahti (aki.sartolahti@student.hamk.fi)
- Vibecky Leinonen (amk1005954@student.hamk.fi)

## Problem
Tourists can feel overwhelmed by the amount of places to visit in helsinki. With limited time they most likely want the best experience and the idea of this app is that it recommends places and it can recommend upcoming events. 

### Intended users
The intended users are tourists or even people that live in a another part of Finland and want to visit Helsinki.

### Problem statement
There are a lot of available events, restaurants, landmarks. The idea is that the tourists can get a great visiting experience without using too much time thinking where to go next.

### Why AI is appropriate
Why does this problem require AI / LLM capabilities rather than traditional deterministic software?

Some deterministic software may be outdated due to places closing or it may recommend events that have already passed. This application uses API's regarding places and upcoming events, so it should always give updated information. 

## Solution

Briefly describe your application, its primary value proposition, and how it addresses the problem statement above.

As stated above, the application will use API's that have information on places in helsinki and upcoming events. The value is that it will give tourist a plan on what to do instead of feeling overwhelmed or lost.

## Main user workflow

1. **User Input:** The user submits a question through the Streamlit user interface. The UI maintains the conversation history in `st.session_state["messages"]` and passes the latest question to `generate_response()` in `src/services/ai_service.py`.

2. **Processing and Routing:** The `ai_service.py` module examines the question using predefined Python logic to determine whether it concerns events and, if applicable, identify a relevant topic, requested date, and number of events.

3. **Data Retrieval:** For event-related questions, the service layer calls functions in `src/services/event_service.py`, which sends HTTP GET requests to the Helsinki Linked Events API. The application retrieves event data within the requested date range, filters out invalid records and events outside that range, removes duplicates, and excludes events without valid information URLs. Topic-based searches use the API's keyword endpoint to identify relevant events. 

4. **Response Preparation:** For event-related questions, the application formats the retrieved event information into a readable list containing event names, start times, and links. For other questions, the application passes the user's question and system instructions to the language model. The system instructions specify that responses should be concise, friendly, in the user's language, and based only on the provided context. Event results are currently formatted by the Python service rather than being converted into a context block for the model to interpret.

5. **Model Response and Output:** For questions handled by the language model, `ollama_client.py` communicates with the locally running Ollama model, `qwen3:1.7b`, and returns the generated response to `ai_service.py`. The service then returns the answer to the Streamlit UI, which displays it to the user. Event-related questions are handled by the event service and formatted into a response that is displayed directly in the UI.

## Architecture

Below is the initial starter architecture. As your project evolves with additional capabilities, replace or extend this diagram in [`docs/architecture.md`](docs/architecture.md).

```text
User
  ↓
Streamlit UI (app/ui.py)
  ↓
Application / AI Service (src/services/ai_service.py)
  ↓
Model Client (src/models/ollama_client.py)
  ↓
Ollama (Local LLM Server)
```

> **Core Architectural Rule:** The user interface must NEVER communicate directly with the model client or Ollama. All interactions must pass through the service layer (`ai_service.py`).

## Model

- **Model used:** e.g., `qwen3:1.7b` (or specified local Ollama model)
- **Selection rationale:** Why was this specific model chosen for your project (e.g., lightweight, performance, context size)? The model was chosen because it is lightweight so it can run easier than heavier models and it should perform well enough for the project.

## Additional AI capability

Select at least one additional capability to implement for your final project:

- [] RAG (Retrieval-Augmented Generation)
- [x] Tools / External API integration
- [ ] Model Context Protocol (MCP)
- [ ] Agentic workflow (Model-selected actions based on observations)
- [ ] Memory / Persistent state
- [ ] Multimodal interaction (Text + Images)
- [x ] Other: Paritally/ not fully implemented were memory state and agent workflow______________________

### Capability justification
Pulling live and verified data directly from the Helsinki Linked Events API makes it so that the user can get up to date information about places and events. 


## Setup

### 1. Create the Conda environment

```bash
conda env create -f environment.yml
```

### 2. Activate the environment

```bash
conda activate dev-ai-project
```

### 3. Configure environment variables

Copy `.env.example` to create your local `.env` configuration file:

On Linux / macOS:
```bash
cp .env.example .env
```

On Windows (Command Prompt / PowerShell):
```powershell
copy .env.example .env
```

Ensure `.env` contains valid values for `OLLAMA_BASE_URL` and `MODEL_NAME`:
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2
```

### 4. Start Ollama

Make sure Ollama is installed and running locally, then pull your configured model:

```bash
ollama run llama3.2
```

### 5. Run the application

Run the application from the root directory of the project:

```bash
python -m app.main
```

Then open your browser at `[http://localhost:11434]`.

### 6. Run automated tests

```bash
pytest
```

## Evaluation

### Methology

Several test cases were composed, where it has a give input and how it would be expected to answer, and written down in a file, each test was automatically run through each iteration of the system, and manually graded based on how the result matched expected behavior.

### Key results

The system generally worked when used as intended, but would have difficulties handling out of scope and adversarial inputs.

## Known limitations

- Highlight known system limitations, unhandled edge cases, or boundaries of current capabilities.

## Future improvements

- List planned feature enhancements, architectural refactorings, or future capabilities.
