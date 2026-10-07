import gradio as gr
from src.services.ai_service import generate_response

def chat_with_history(message, history):
    history = history or []

    response = generate_response(
        message,
        history=history
    )

    updated_history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": response},
    ]

    return response, updated_history

def build_ui() -> gr.Blocks:
    """
    Constructs the Gradio web interface.
    
    Architectural Principle: The UI communicates strictly with `generate_response()`
    in the AI service layer and never directly with Ollama or the model client.
    """
    with gr.Blocks(title="AI Application Starter") as demo:
        history_state = gr.State([])

        gr.Markdown(
            """
            # AI Application Starter
            
            Welcome to the AI Application Starter repository.
            Type a prompt below to interact with your local AI service.
            """
        )

        with gr.Row():
            user_input = gr.Textbox(
                lines=3,
                placeholder="Type your message here...",
                label="User Prompt",
            )

        submit_btn = gr.Button("Send", variant="primary")

        with gr.Row():
            output_box = gr.Textbox(
                lines=8,
                label="AI Response",
                interactive=False,
            )

        # Connect UI actions exclusively to the service layer function
        submit_btn.click(
            fn=chat_with_history,
            inputs=[user_input, history_state],
            outputs=[output_box, history_state],
        )
        user_input.submit(
            fn=chat_with_history,
            inputs=[user_input, history_state],
            outputs=[output_box, history_state],
        )

    return demo
