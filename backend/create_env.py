#!/usr/bin/env python3
"""
Helper script to create .env file from template
"""
import os
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"
    
    if env_path.exists():
        print("✅ .env file already exists")
        return
    
    # Create .env.example template
    template = """# OpenRouter API Configuration (REQUIRED)
# Get your API key from https://openrouter.ai/
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Model Selection (Optional)
# Default: openai/gpt-4o-mini
OPENROUTER_MODEL=openai/gpt-4o-mini

# Database Configuration (Optional)
DATABASE_URL=sqlite:///./naio.db

# Environment (Optional)
ENVIRONMENT=development

# Groq API Configuration (Optional)
# GROQ_API_KEY=your_groq_api_key_here

# Redis Configuration (Optional)
# REDIS_URL=redis://localhost:6379
"""
    
    # Create .env.example
    if not env_example_path.exists():
        env_example_path.write_text(template)
        print(f"✅ Created .env.example template at {env_example_path}")
    
    # Create .env from template
    env_path.write_text(template)
    print(f"✅ Created .env file at {env_path}")
    print("\n⚠️  IMPORTANT: Edit backend/.env and add your OPENROUTER_API_KEY")
    print("   Get your API key from: https://openrouter.ai/")

if __name__ == "__main__":
    create_env_file()


