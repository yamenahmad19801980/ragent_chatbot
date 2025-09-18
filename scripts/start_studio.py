#!/usr/bin/env python3
"""
LangGraph Studio startup script for Ragent Chatbot development.
This script ensures all dependencies are installed and starts LangGraph Studio.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'langgraph-studio',
        'langchain',
        'langchain-core',
        'gradio',
        'pandas',
        'requests',
        'aiohttp'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        return False
    
    return True

def install_dependencies():
    """Install missing dependencies."""
    print("\n🔧 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, cwd=Path(__file__).parent.parent)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("📝 Please create a .env file with required variables:")
        print("   QWEN_API_KEY=your_api_key")
        print("   TAVILY_API_KEY=your_api_key")
        print("   EMAIL=your_email")
        print("   PASSWORD=your_password")
        return False
    
    # Check for required variables
    required_vars = ['QWEN_API_KEY', 'TAVILY_API_KEY', 'EMAIL', 'PASSWORD']
    missing_vars = []
    
    with open(env_path, 'r') as f:
        env_content = f.read()
        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file configured correctly")
    return True

def test_graph_compilation():
    """Test if the graph can be compiled successfully."""
    print("\n🧪 Testing graph compilation...")
    try:
        # Change to project root
        project_root = Path(__file__).parent.parent
        os.chdir(project_root)
        
        # Test import and compilation
        from agent import get_compiled_graph
        graph = get_compiled_graph()
        print("✅ Graph compiled successfully")
        return True
    except Exception as e:
        print(f"❌ Graph compilation failed: {e}")
        return False

def start_langgraph_studio(port=8123, debug=False):
    """Start LangGraph Studio."""
    print(f"\n🚀 Starting LangGraph Studio on port {port}...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Prepare command
    cmd = ['langgraph-studio', '--config', 'studio/langgraph.json', '--port', str(port)]
    
    if debug:
        cmd.append('--debug')
        os.environ['LANGGRAPH_DEBUG'] = '1'
    
    try:
        print(f"🌐 Studio will be available at: http://localhost:{port}")
        print("📖 See studio/README.md for usage instructions")
        print("\n" + "="*50)
        print("🎯 LangGraph Studio is starting...")
        print("="*50)
        
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 LangGraph Studio stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start LangGraph Studio: {e}")
        return False
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Start LangGraph Studio for Ragent Chatbot')
    parser.add_argument('--port', type=int, default=8123, help='Port to run LangGraph Studio on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--skip-checks', action='store_true', help='Skip dependency and configuration checks')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies and exit')
    
    args = parser.parse_args()
    
    print("🤖 Ragent Chatbot - LangGraph Studio Launcher")
    print("=" * 50)
    
    if args.install_deps:
        if not check_python_version():
            sys.exit(1)
        if install_dependencies():
            print("\n✅ Dependencies installed successfully!")
            print("You can now run: python scripts/start_studio.py")
        else:
            print("\n❌ Failed to install dependencies")
            sys.exit(1)
        return
    
    if not args.skip_checks:
        # Run all checks
        if not check_python_version():
            sys.exit(1)
        
        if not check_dependencies():
            print("\n🔧 Installing missing dependencies...")
            if not install_dependencies():
                print("❌ Failed to install dependencies. Please install manually:")
                print("   pip install -r requirements.txt")
                sys.exit(1)
        
        if not check_env_file():
            print("\n❌ Please configure your .env file before starting LangGraph Studio")
            sys.exit(1)
        
        if not test_graph_compilation():
            print("\n❌ Graph compilation failed. Please check your code")
            sys.exit(1)
    
    # Start LangGraph Studio
    start_langgraph_studio(args.port, args.debug)

if __name__ == "__main__":
    main()
