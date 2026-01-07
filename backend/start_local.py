#!/usr/bin/env python3
"""
Local development server for AI Caseworker Backend
Run this for local testing before deploying to Render.com
"""

import os
import sys
import uvicorn
from pathlib import Path

def setup_environment():
    """Set up environment variables for local development."""
    # Add backend directory to Python path
    backend_dir = Path(__file__).parent
    sys.path.insert(0, str(backend_dir))
    
    # Set default environment variables if not already set
    env_vars = {
        'AZURE_OPENAI_ENDPOINT': 'https://your-resource.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'your-api-key-here',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'gpt-4',
        'PORT': '8000'
    }
    
    for key, default_value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = default_value
            print(f"⚠️  Set {key} to default value. Update for production!")

def main():
    """Start the local development server."""
    print("🚀 Starting AI Caseworker Backend (Local Development)")
    print("=" * 60)
    
    setup_environment()
    
    # Check if model file exists
    model_path = Path(__file__).parent / 'welfare_risk_model.pkl'
    if not model_path.exists():
        print(f"❌ Model file not found: {model_path}")
        print("   Make sure welfare_risk_model.pkl is in the backend/ directory")
        sys.exit(1)
    
    print(f"✅ Model file found: {model_path}")
    print(f"🌐 Server will start at: http://localhost:{os.getenv('PORT', 8000)}")
    print(f"📚 API docs available at: http://localhost:{os.getenv('PORT', 8000)}/docs")
    print("=" * 60)
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv('PORT', 8000)),
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()