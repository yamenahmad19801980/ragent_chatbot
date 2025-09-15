"""
Simple deployment script for Hugging Face Spaces
"""

import os
import sys
import subprocess
from pathlib import Path

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🏠 Ragent Chatbot - Deploying to Hugging Face Spaces")
    print("=" * 55)
    
    # Set up environment
    # Get token from environment variable or user input
    token = os.environ.get('HF_TOKEN')
    if not token:
        token = input("Enter your Hugging Face token: ")
    os.environ['HF_TOKEN'] = token
    
    # Install required packages
    print("📦 Installing required packages...")
    packages = ['huggingface_hub', 'requests']
    for package in packages:
        if install_package(package):
            print(f"✅ Installed {package}")
        else:
            print(f"❌ Failed to install {package}")
            return
    
    # Import after installation
    try:
        from huggingface_hub import HfApi
        print("✅ Hugging Face Hub library ready")
    except ImportError as e:
        print(f"❌ Failed to import Hugging Face Hub: {e}")
        return
    
    # Initialize API
    api = HfApi(token=os.environ['HF_TOKEN'])
    repo_id = 'yamen19801980/ragent_chatbot'
    
    print(f"🔄 Uploading files to {repo_id}...")
    
    # Files to upload
    files_to_upload = [
        'app.py',
        'agent.py', 
        'config.py',
        'tool_registry.py',
        'requirements.txt',
        'README.md',
        'prompts/templates.py',
        'services/__init__.py',
        'services/device_service.py',
        'utils/__init__.py',
        'utils/normalizer.py',
        'tools/__init__.py',
        'tools/device_tools.py',
        'tools/base_tool.py',
        'tools/web_search_tool.py',
        'domain/api_client.py',
        'domain/objects.py',
        'llm/__init__.py',
        'llm/qwen_llm.py',
        'llm/langsmith_config.py',
        'memory/__init__.py',
        'memory/chat_memory.py',
        'data/device_mappings.csv'
    ]
    
    # Upload files
    uploaded_count = 0
    failed_count = 0
    
    for file_path in files_to_upload:
        if Path(file_path).exists():
            try:
                api.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=file_path,
                    repo_id=repo_id,
                    repo_type='space',
                    commit_message=f'Upload {file_path} - Refactored code'
                )
                print(f"✅ Uploaded: {file_path}")
                uploaded_count += 1
            except Exception as e:
                print(f"❌ Failed to upload {file_path}: {str(e)}")
                failed_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
            failed_count += 1
    
    print("\n" + "=" * 55)
    print(f"📊 Upload Summary:")
    print(f"✅ Successfully uploaded: {uploaded_count} files")
    print(f"❌ Failed uploads: {failed_count} files")
    
    if uploaded_count > 0:
        print(f"\n🎉 Upload completed!")
        print(f"🌐 Your Space: https://huggingface.co/spaces/{repo_id}")
        print("🔄 The Space will automatically rebuild with your new code")
    else:
        print("\n❌ No files were uploaded successfully")

if __name__ == "__main__":
    main()
