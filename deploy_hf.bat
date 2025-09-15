@echo off
echo 🏠 Ragent Chatbot - Deploying to Hugging Face Spaces
echo ==================================================

echo 📦 Installing required packages...
python -m pip install huggingface_hub requests --quiet

echo 🚀 Starting deployment...
python -c "
import os
import sys
from pathlib import Path

# Set up environment
# Get token from environment variable or user input
token = os.environ.get('HF_TOKEN')
if not token:
    token = input('Enter your Hugging Face token: ')
os.environ['HF_TOKEN'] = token

# Install huggingface_hub if not available
try:
    from huggingface_hub import HfApi, Repository
    print('✅ Hugging Face Hub library found')
except ImportError:
    print('📦 Installing Hugging Face Hub...')
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'huggingface_hub'])
    from huggingface_hub import HfApi, Repository

# Initialize API
api = HfApi(token=os.environ['HF_TOKEN'])
repo_id = 'yamen19801980/ragent_chatbot'

print(f'🔄 Uploading files to {repo_id}...')

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
            print(f'✅ Uploaded: {file_path}')
            uploaded_count += 1
        except Exception as e:
            print(f'❌ Failed to upload {file_path}: {str(e)}')
    else:
        print(f'⚠️  File not found: {file_path}')

print(f'\\n🎉 Upload completed! {uploaded_count} files uploaded successfully')
print(f'🌐 Your Space: https://huggingface.co/spaces/{repo_id}')
print('🔄 The Space will automatically rebuild with your new code')
"

echo.
echo ✅ Deployment completed!
echo 🌐 Visit your Space: https://huggingface.co/spaces/yamen19801980/ragent_chatbot
pause
