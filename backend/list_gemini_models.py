"""
List all available Gemini models for your API key
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import google.generativeai as genai
from app.config import settings

print("=" * 80)
print("  CHECKING AVAILABLE GEMINI MODELS")
print("=" * 80)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

print(f"\nAPI Key: {settings.GEMINI_API_KEY[:20]}...")
print("\nListing all available models:\n")

try:
    for model in genai.list_models():
        # Check if model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            print(f"[OK] {model.name}")
            print(f"     Display Name: {model.display_name}")
            print(f"     Description: {model.description}")
            print(f"     Supported methods: {', '.join(model.supported_generation_methods)}")
            print()

    print("=" * 80)
    print("\nUse one of the model names above in your .env file")
    print("Example: GEMINI_MODEL=gemini-1.5-flash")
    print("=" * 80)

except Exception as e:
    print(f"[ERROR] Failed to list models: {e}")
    import traceback
    traceback.print_exc()
