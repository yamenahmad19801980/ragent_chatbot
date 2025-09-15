# Ragent Chatbot - Deploy to Hugging Face Spaces
Write-Host "🏠 Ragent Chatbot - Deploying to Hugging Face Spaces" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Set environment variable (user will be prompted for token)
# $env:HF_TOKEN = "your_token_here"

Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
try {
    python -m pip install huggingface_hub requests --quiet
    Write-Host "✅ Packages installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install packages: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Starting deployment..." -ForegroundColor Yellow

# Python script to upload files
$pythonScript = @"
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
    from huggingface_hub import HfApi
    print('✅ Hugging Face Hub library found')
except ImportError:
    print('📦 Installing Hugging Face Hub...')
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'huggingface_hub'])
    from huggingface_hub import HfApi

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
"@

# Execute the Python script
try {
    $pythonScript | python
    Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "🌐 Visit your Space: https://huggingface.co/spaces/yamen19801980/ragent_chatbot" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nPress any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
