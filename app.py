"""
Main application entry point for the ragent_chatbot.
Gradio interface for the smart home chatbot.
"""

import gradio as gr
from agent import RagentChatbot
from utils.logger import get_logger

# Initialize chatbot instance
chatbot = RagentChatbot()
logger = get_logger(__name__)

def chat_fn(message, history):
    """Chat function for Gradio interface."""
    return chatbot.chat(message, history)

def re_login():
    """Re-login to refresh access token."""
    try:
        logger.info("🔄 Re-login button clicked - attempting to refresh access token...")
        success = chatbot.refresh_token()
        if success:
            logger.info("✅ Access token refreshed successfully")
            status = chatbot.get_token_status()
            logger.info(f"New status: {status}")
            return status
        else:
            logger.error("❌ Failed to refresh access token")
            return "❌ Login failed. Please check your credentials."
    except Exception as e:
        logger.error(f"❌ Re-login error: {e}")
        return f"❌ Login error: {str(e)}"

def check_token():
    """Check if the current token is valid."""
    try:
        logger.info("🔍 Check token button clicked - checking token validity...")
        is_valid = chatbot.check_token_validity()
        if is_valid:
            logger.info("✅ Token is valid")
            status = chatbot.get_token_status()
            logger.info(f"Status: {status}")
            return status
        else:
            logger.warning("⚠️ Token is invalid")
            return "❌ Token is invalid. Please re-login."
    except Exception as e:
        logger.error(f"❌ Error checking token: {e}")
        return f"❌ Error checking token: {str(e)}"

def main():
    """Main application function."""
    logger.info("Initializing Gradio interface...")
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
        
        # Re-login section
        gr.Markdown("### 🔐 Token Management")
        logger.info("Creating re-login buttons...")
        with gr.Row():
            relogin_btn = gr.Button("🔄 Re-login", variant="primary", scale=1, size="lg")
            check_token_btn = gr.Button("🔍 Check Token", variant="secondary", scale=1, size="lg")
            login_status = gr.Textbox(
                value=chatbot.get_token_status(),
                label="Connection Status",
                interactive=False,
                scale=2
            )
        logger.info("Re-login buttons created successfully")
        
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
        
        logger.info("Setting up re-login button event handler...")
        relogin_btn.click(
            re_login,
            outputs=[login_status]
        )
        
        logger.info("Setting up check token button event handler...")
        check_token_btn.click(
            check_token,
            outputs=[login_status]
        )
        
        logger.info("All event handlers set up successfully")

    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
