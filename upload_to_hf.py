"""
Upload refactored code to Hugging Face Spaces using access token
"""

import os
import requests
import json
from pathlib import Path

# Hugging Face configuration
# Get token from environment variable or user input
HF_TOKEN = os.environ.get('HF_TOKEN')
if not HF_TOKEN:
    HF_TOKEN = input("Enter your Hugging Face token: ")
REPO_ID = "yamen19801980/ragent_chatbot"
REPO_TYPE = "space"

# API endpoints
HF_API_BASE = "https://huggingface.co/api"
HF_UPLOAD_BASE = "https://huggingface.co"

def upload_file_to_hf(file_path, repo_id, token, repo_type="space"):
    """Upload a single file to Hugging Face repository"""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Prepare upload URL
        upload_url = f"{HF_UPLOAD_BASE}/{repo_type}s/{repo_id}/upload"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Prepare data
        data = {
            "path": file_path,
            "content": content,
            "commit_message": f"Upload {file_path} - Refactored code"
        }
        
        # Make request
        response = requests.post(upload_url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"✅ Successfully uploaded: {file_path}")
            return True
        else:
            print(f"❌ Failed to upload {file_path}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading {file_path}: {str(e)}")
        return False

def upload_directory_to_hf(directory_path, repo_id, token, repo_type="space"):
    """Upload all files from directory to Hugging Face repository"""
    directory = Path(directory_path)
    uploaded_files = []
    failed_files = []
    
    # Files to upload (excluding unnecessary files)
    files_to_upload = [
        "app.py",
        "agent.py",
        "config.py",
        "tool_registry.py",
        "requirements.txt",
        "README.md",
        "prompts/templates.py",
        "services/__init__.py",
        "services/device_service.py",
        "utils/__init__.py",
        "utils/normalizer.py",
        "tools/__init__.py",
        "tools/device_tools.py",
        "tools/base_tool.py",
        "tools/web_search_tool.py",
        "domain/api_client.py",
        "domain/objects.py",
        "llm/__init__.py",
        "llm/qwen_llm.py",
        "llm/langsmith_config.py",
        "memory/__init__.py",
        "memory/chat_memory.py",
        "data/device_mappings.csv"
    ]
    
    print(f"🚀 Starting upload to {repo_id}...")
    print(f"📁 Uploading from: {directory}")
    print("-" * 50)
    
    for file_path in files_to_upload:
        full_path = directory / file_path
        
        if full_path.exists():
            if upload_file_to_hf(str(full_path), repo_id, token, repo_type):
                uploaded_files.append(file_path)
            else:
                failed_files.append(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("-" * 50)
    print(f"📊 Upload Summary:")
    print(f"✅ Successfully uploaded: {len(uploaded_files)} files")
    print(f"❌ Failed uploads: {len(failed_files)} files")
    
    if uploaded_files:
        print(f"\n✅ Uploaded files:")
        for file in uploaded_files:
            print(f"   - {file}")
    
    if failed_files:
        print(f"\n❌ Failed files:")
        for file in failed_files:
            print(f"   - {file}")
    
    return len(failed_files) == 0

def main():
    """Main function to upload refactored code"""
    print("🏠 Ragent Chatbot - Hugging Face Upload")
    print("=" * 50)
    
    # Check if token is provided
    if not HF_TOKEN:
        print("❌ Error: Hugging Face token not provided")
        return
    
    # Upload directory
    success = upload_directory_to_hf(".", REPO_ID, HF_TOKEN, REPO_TYPE)
    
    if success:
        print("\n🎉 Upload completed successfully!")
        print(f"🌐 Your Space: https://huggingface.co/spaces/{REPO_ID}")
        print("🔄 The Space will automatically rebuild with your new code")
    else:
        print("\n⚠️  Upload completed with some errors")
        print("Please check the failed files and try again")

if __name__ == "__main__":
    main()
