# Project decisions

Use this decision log to document significant technical and architectural choices made by your team during development.

## Decision 1 — Model selection

**Decision: Ollama qwen3:1.7b**

**Alternatives considered:* qwen3:4b, qwen3:8b*

**Why we chose this: ** We chose a model that had less parameters because otherwise the generation of results was too slow.

---


## Decision 2 — Additional AI capability

**Decision:** Tools & External APIs. The event_service.py calls the Helsinki Linked Events API and Geoapify API. The application selects and calls the event service or recommends a restaurant/place based on the user's question. 
For agent work flow there is basic routing. ai_service.py classifies questions using keywords and routes them to the event or restaurant/places API. There is however no dynamic multi-step reasoning workflow.
As for memory state it is only implemented partially. The Streamlit UI stores messages in st.session_state["messages"] so it perserves conversation messages during the current session, but the AI service does not automatically send the conversation history to Ollama so there is no memory across sessions.

**Why it is needed:** These implementations were needed for a working application that we set out to do. The course also required to add at least one additional AI capability.

**Alternatives considered:** We considered adding RAG but came to decision to not add it in the end.

---

## Decision 3 — Architecture

**Decision:**

**Why:**
