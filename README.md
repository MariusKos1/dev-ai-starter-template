# Visiting plan assistant for restaraunts and upcoming events for the city of Helsinki

Starter template for the **Development of AI Applications** course final group project.

## Team members

- Marius Koskinen (marius.koskinen@student.hamk.fi)
- Pauliina Touruvirta (anna-pauliina.touruvirta@student.hamk.fi)
- Aki Sartolahti (aki.sartolahti@student.hamk.fi)
- Vibecky Leinonen (amk1005954@student.hamk.fi)

## Problem
Tourists can feel overwhelmed by the amount of places to visit in helsinki. With limited time they most likely want the best experience and the idea of this app is that it recommends places based on user reviews and it can recommend upcoming events. 

### Intended users
The intended users are tourists or even people that live in a another part of Finland and want to visit Helsinki.

### Problem statement
There are a lot of available events, restaurants, landmarks. The idea is that the tourists can get a great visiting experience without using too much time thinking where to go next.

### Why AI is appropriate
Why does this problem require AI / LLM capabilities rather than traditional deterministic software?

Some deterministic software may be outdated due to places closing or it may recommend events that have already passed. This application use API's regarding places and upcoming events, so it should always give updated information. 

## Solution

Briefly describe your application, its primary value proposition, and how it addresses the problem statement above.

As stated above, the application will use API's that have information on places in helsinki and upcoming events. The value is that it will give tourist a plan on what to do instead of feeling overwhelmed or lost.

## Main user workflow

1. **User Input:** The user submits a prompt or query via the Streamlit user interface.
2. **Processing:** The ai_service.py looks at the query and sends a quick prompt to qwen3:8b and asks it to classify the intent into: restaurants, events, or both.
3. **Data retrieval:** The service layer performs an HTTP GET requests. For restaurants it fetches from the Google Places/MyHelsinki API and ideally it filters out places with low user review scores for example minrating=4.5. For events it fetches upcoming events from the Linked Events API and ideally it filters to out everything that is below the current date and also everything that is more than 3 days away. The Python script should fetch a raw json payload from the Linked Events API and also only extract the information that the model needs.
4. **Promt handling:** After processing the json's the application will turn it into a context block. Instructions will be added to the model so it behaves correctly. 
5. **Model Response:** The model client calls Ollama locally and returns the response back through the service layer to the UI.

## Architecture

Below is the initial starter architecture. As your project evolves with additional capabilities, replace or extend this diagram in [`docs/architecture.md`](docs/architecture.md).

```text
User
  ↓
Streamlit UI (app/ui.py)
  ↓
Application / AI Service (src/services/ai_service.py)
  ↓
Model Client (src/models/model_client.py)
  ↓
Ollama (Local LLM Server)
```

> **Core Architectural Rule:** The user interface must NEVER communicate directly with the model client or Ollama. All interactions must pass through the service layer (`ai_service.py`).

## Model

- **Model used:** e.g., `qwen3:8b` (or specified local Ollama model)
- **Selection rationale:** Why was this specific model chosen for your project (e.g., lightweight, performance, context size)? The model was chosen because it is lightweight so it can run easier than heavier models and it should perform well enough for the project.

## Additional AI capability

Select at least one additional capability to implement for your final project:

- [x] RAG (Retrieval-Augmented Generation)
- [x] Tools / External API integration
- [ ] Model Context Protocol (MCP)
- [ ] Agentic workflow (Model-selected actions based on observations)
- [ ] Memory / Persistent state
- [ ] Multimodal interaction (Text + Images)
- [ ] Other: ______________________

### Capability justification
Pulling live and verified data directly from the MyHelsinki Open API and the Helsinki Linked Events API makes it so that the user can get up to date information about places and events. The RAG pipeline acts as a data filter that provides the local LLM with current information (For example only pulling restaurants with a minrating=4.5 that are verified as open_now). This turns the AI from a normal text generator into an application that works with up to date information.


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

Then open your browser at `http://localhost:7860`.

### 6. Run automated tests

```bash
pytest
```

## Evaluation

Describe your evaluation methodology and summarize key results. Starter test cases can be found in [`evaluation/test_cases.json`](evaluation/test_cases.json).

Refer to [`evaluation/README.md`](evaluation/README.md) for guidelines on defining success, edge cases, and failure scenarios.

## Known limitations

- Highlight known system limitations, unhandled edge cases, or boundaries of current capabilities.

## Future improvements

- List planned feature enhancements, architectural refactorings, or future capabilities.
