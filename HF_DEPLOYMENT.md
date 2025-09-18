# 🚀 Deploy to Hugging Face Spaces

## Your Hugging Face Space
**URL**: https://huggingface.co/spaces/yamen19801980/ragent_chatbot

## Quick Deployment (Manual Upload)

### Step 1: Go to Your Space
1. Visit: https://huggingface.co/spaces/yamen19801980/ragent_chatbot
2. Click **"Files"** tab
3. Click **"Add file"** → **"Upload files"**

### Step 2: Upload Core Files
Upload these files one by one:

**Main Application:**
- `app.py` - Gradio interface
- `requirements.txt` - Dependencies
- `README.md` - Documentation

**Core Logic:**
- `agent.py` - Main chatbot agent
- `config.py` - Configuration
- `tool_registry.py` - Tool management

**Services (Create folders first):**
- `prompts/templates.py` - Centralized prompts
- `services/__init__.py` - Service package
- `services/device_service.py` - Device operations
- `utils/__init__.py` - Utils package
- `utils/normalizer.py` - Message processing

**Tools:**
- `tools/__init__.py` - Tools package
- `tools/device_tools.py` - Device tools
- `tools/base_tool.py` - Base tool class
- `tools/web_search_tool.py` - Web search tool

**Domain:**
- `domain/api_client.py` - API client
- `domain/objects.py` - Data models

**LLM:**
- `llm/__init__.py` - LLM package
- `llm/qwen_llm.py` - Qwen integration
- `llm/langsmith_config.py` - LangSmith config

**Memory:**
- `memory/__init__.py` - Memory package
- `memory/chat_memory.py` - Chat memory

**Data:**
- `data/device_mappings.csv` - Device mappings

### Step 3: Wait for Build
- The Space will automatically rebuild
- Check the **"Logs"** tab for any errors
- Your app should be ready in a few minutes

## Alternative: Connect GitHub Repository

### Step 1: Go to Space Settings
1. Visit your Space
2. Click **"Settings"** tab
3. Scroll to **"Repository"** section

### Step 2: Connect GitHub
1. Click **"Connect to GitHub"**
2. Select repository: `yamenahmad19801980/ragent_chatbot`
3. Select branch: `main`
4. Click **"Connect"**

### Step 3: Automatic Sync
- Your Space will automatically sync with GitHub
- Changes will be deployed automatically

## 🔧 Environment Variables (Optional)

If you need API credentials:
1. Go to **Settings** → **Variables and secrets**
2. Add your Syncrow API credentials:
   - `SYNCROW_EMAIL`
   - `SYNCROW_PASSWORD`
   - `PROJECT_UUID`
   - `COMMUNITY_UUID`
   - `SPACE_UUID`
   - `USER_UUID`

## ✅ Test Your Deployment

After deployment, test with these commands:
- "Turn on the kitchen light"
- "What's the temperature?"
- "Schedule AC for 6 PM"
- "Make it cozy"
- "How's the weather today?"

## 🎉 Success!

Your refactored Ragent Chatbot is now deployed on Hugging Face Spaces!

**Features Ready:**
- ✅ Smart device control
- ✅ Status queries
- ✅ Device scheduling
- ✅ Scene management
- ✅ Web search
- ✅ Conversational AI
- ✅ Clean, refactored code
