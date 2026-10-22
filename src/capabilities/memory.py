"""
Optional project capability: Memory & Persistent Conversation State.

Implement this module only if this capability is relevant to your application's
user problem. Remove the file if the capability is not used.

Conceptual Overview:
-------------------
Memory enables an application to retain conversational context across multiple user interactions
or persist state between user sessions.

Key concepts when implementing memory:
1. Short-term Memory (Chat History): Maintaining an ordered list of user and assistant
   messages within the current session and appending them to model requests.
2. Context Window Management: Truncating, summarizing, or pruning history when it exceeds
   the model's maximum context length.
3. Long-term / Persistent Memory: Storing user preferences, session history, or key facts
   in local files or persistent state stores.

Note:
-----
Keep memory implementations simple and relevant to the user's workflow needs.


# Implement custom conversation memory or state management below if selected.

The application uses Streamlit's session state to maintain short-term conversation history during the current user session. The conversation is stored in st.session_state["messages"], which contains an ordered list of user messages and assistant responses. 
This allows previous messages to remain visible as the user interacts with the application.
Currently, the conversation history is used to display previous messages in the user interface. Only the latest user question is passed to the language model, so previous messages are not yet included as context when generating responses.
The application does not implement long-term memory or persistent storage of conversations. The conversation state is temporary and is not intended to retain user preferences or conversation history between separate sessions.
"""
