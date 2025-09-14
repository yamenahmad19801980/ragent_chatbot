"""
Main application entry point for the ragent_chatbot.
Gradio interface for the smart home chatbot.
"""

import gradio as gr
from agent import RagentChatbot

def create_chatbot():
    """Create and return a chatbot instance."""
    return RagentChatbot()

def chat_fn(message, history):
    """Chat function for Gradio interface."""
    chatbot = create_chatbot()
    return chatbot.chat(message, history)

def main():
    """Main application function."""
    with gr.Blocks(title="Smart Home Assistant") as demo:
        gr.Markdown("# 🏠 Smart Home Assistant")
        gr.Markdown("Your intelligent IoT assistant. Control devices, schedule actions, and get help with your smart home!")
        
        with gr.ChatInterface(
            chat_fn,
            chatbot=gr.Chatbot(
                height=400,
                show_copy_button=True,
                avatar_images=("👤", "🤖")
            ),
            textbox=gr.Textbox(
                placeholder="Ask me to control your devices, schedule actions, or just chat!",
                container=False,
                scale=7
            ),
            submit_btn="Send",
            retry_btn="🔄 Retry",
            undo_btn="↩️ Undo",
            clear_btn="🗑️ Clear",
        ):
            pass
        
        # Add some examples
        gr.Examples(
            examples=[
                "Turn on the living room lights",
                "Set the temperature to 72 degrees",
                "What's the status of the kitchen switch?",
                "Schedule the AC to turn on at 8 AM tomorrow",
                "Activate movie night scene",
                "What's the weather like today?",
                "Tell me a joke"
            ],
            inputs=gr.Textbox(placeholder="Type your message here...")
        )

    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
