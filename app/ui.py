import gradio as gr
from src.services.ai_service import generate_response


def build_ui() -> gr.Blocks:
    """
    Constructs the Gradio web interface.
    
    Architectural Principle: The UI communicates strictly with `generate_response()`
    in the AI service layer and never directly with Ollama or the model client.
    """
    with gr.Blocks(title="Helsinki Visit Assistant") as demo:
        gr.Markdown(
            """
            # Helsinki Visit Assistant
            
            Discover restaurants and upcoming events in Helsinki with the help of our AI assistant.
            Get personalized recommendations and travel plans based on your interests.
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
            fn=generate_response,
            inputs=user_input,
            outputs=output_box,
        )
        user_input.submit(
            fn=generate_response,
            inputs=user_input,
            outputs=output_box,
        )

    return demo
