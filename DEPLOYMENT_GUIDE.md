# 🚀 Deployment Guide - Hugging Face Spaces

## Quick Deployment Options

### Option 1: Manual Upload (Easiest)
1. Go to your [Hugging Face Space](https://huggingface.co/spaces/yamen19801980/ragent_chatbot)
2. Click **"Files"** tab
3. Upload these key files:
   - `app.py` (main application)
   - `requirements.txt` (dependencies)
   - `README.md` (documentation)
   - All files from `prompts/`, `services/`, `utils/`, `tools/`, `domain/`, `llm/`, `memory/` folders

### Option 2: Using Python Script
1. **Set your token** (replace with your actual token):
   ```bash
   set HF_TOKEN=your_token_here
   ```

2. **Run the deployment script**:
   ```bash
   python deploy_simple.py
   ```

### Option 3: Using Batch Script (Windows)
1. **Set your token** in the script or environment
2. **Run**:
   ```bash
   deploy_hf.bat
   ```

### Option 4: Using PowerShell
1. **Set your token** in the script or environment
2. **Run**:
   ```powershell
   .\deploy_hf.ps1
   ```

## 🔧 Required Files for Deployment

### Core Files:
- `app.py` - Main Gradio application
- `requirements.txt` - Python dependencies
- `README.md` - Space documentation

### Application Files:
- `agent.py` - Main chatbot agent
- `config.py` - Configuration settings
- `tool_registry.py` - Tool management

### Service Files:
- `prompts/templates.py` - Centralized prompts
- `services/device_service.py` - Device operations
- `utils/normalizer.py` - Message processing

### Supporting Files:
- `tools/` - All tool files
- `domain/` - API client and objects
- `llm/` - LLM integration
- `memory/` - Chat memory
- `data/device_mappings.csv` - Device data

## 🌐 After Deployment

1. **Visit your Space**: https://huggingface.co/spaces/yamen19801980/ragent_chatbot
2. **Check the logs** if there are any issues
3. **Test the interface** with sample commands
4. **Set environment variables** if needed (in Space settings)

## 🔑 Environment Variables (Optional)

If you need to set environment variables in your Space:
1. Go to **Settings** → **Variables and secrets**
2. Add your Syncrow API credentials:
   - `SYNCROW_EMAIL`
   - `SYNCROW_PASSWORD`
   - `PROJECT_UUID`
   - `COMMUNITY_UUID`
   - `SPACE_UUID`
   - `USER_UUID`

## ✅ Verification

After deployment, your Space should:
- ✅ Show the Gradio interface
- ✅ Display the updated README
- ✅ Have all the refactored code
- ✅ Be ready for testing

## 🎯 Test Commands

Try these commands in your deployed Space:
- "Turn on the kitchen light"
- "What's the temperature?"
- "Schedule AC for 6 PM"
- "Make it cozy"
- "How's the weather today?"

---

**Your refactored code is ready for deployment! 🚀**
