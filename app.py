"""
Main application entry point for the ragent_chatbot.
Gradio interface for the smart home chatbot.
"""

import gradio as gr
from agent import RagentChatbot

# Initialize chatbot instance
chatbot = RagentChatbot()

def chat_fn(message, history):
    """Chat function for Gradio interface."""
    return chatbot.chat(message, history)

def main():
    """Main application function."""
    with gr.Blocks(title="Smart Home Assistant") as demo:
        gr.Markdown("# 🏠 Smart Home Assistant")
        gr.Markdown("Your intelligent IoT assistant. Control devices, schedule actions, and get help with your smart home!")
        
        # Simple chatbot interface
        chatbot_interface = gr.Chatbot(
            label="Chat with your Smart Home Assistant",
            height=500,
            show_copy_button=True,
            type="messages"
        )
        
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Ask me to control your devices, schedule actions, or just chat!",
                label="Your message",
                scale=4
            )
            send_btn = gr.Button("Send", variant="primary", scale=1)
            clear_btn = gr.Button("Clear", variant="secondary", scale=1)
        
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
            inputs=msg_input,
            label="Try these examples:"
        )
        
        # Event handlers
        def respond(message, history):
            if message.strip() == "":
                return history, ""
            
            response = chat_fn(message, history)
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response})
            return history, ""
        
        def clear_chat():
            return []
        
        # Connect events
        send_btn.click(
            respond,
            inputs=[msg_input, chatbot_interface],
            outputs=[chatbot_interface, msg_input]
        )
        
        msg_input.submit(
            respond,
            inputs=[msg_input, chatbot_interface],
            outputs=[chatbot_interface, msg_input]
        )
        
        clear_btn.click(
            clear_chat,
            outputs=[chatbot_interface]
        )

    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
