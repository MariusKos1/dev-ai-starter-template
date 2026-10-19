
import streamlit as st
import traceback

from src.services.ai_service import generate_response


# Configure the Streamlit page
st.set_page_config(
    page_title="Helsinki AI Tourist Assistant",
    page_icon="🇫🇮",
    layout="centered"
)

st.title("🇫🇮 Helsinki AI Tourist Assistant")
st.write(
    "Ask me about restaurants, attractions, "
    "and events in Helsinki!"
)


# Initialize the conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept a new question
question = st.chat_input(
    "What would you like to know about Helsinki?"
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = generate_response(question)
            except Exception as error:
                traceback.print_exc()
                answer = (
                    f"Unexpected error: {type(error).__name__}: {error}"
                )

        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
