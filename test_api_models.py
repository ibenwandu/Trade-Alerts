"""Test API models to find working model names"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("API Model Diagnostic Tool")
print("=" * 60)

# Test Gemini
print("\n🔍 Testing Gemini...")
try:
    import google.generativeai as genai
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not set")
    else:
        print(f"✅ API Key found: {api_key[:10]}...")
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n📋 Listing available Gemini models:")
        try:
            models = genai.list_models()
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    print(f"  ✅ {model.name}")
        except Exception as e:
            print(f"  ⚠️  Could not list models: {e}")
        
        # Test specific models
        test_models = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-latest',
        ]
        
        print("\n🧪 Testing specific models:")
        for model_name in test_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello")
                print(f"  ✅ {model_name}: WORKS")
                break
            except Exception as e:
                print(f"  ❌ {model_name}: {str(e)[:80]}")
except ImportError:
    print("❌ google-generativeai not installed")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Claude
print("\n" + "=" * 60)
print("🔍 Testing Claude...")
try:
    from anthropic import Anthropic
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
    else:
        print(f"✅ API Key found: {api_key[:10]}...")
        client = Anthropic(api_key=api_key)
        
        # Test specific models
        test_models = [
            'claude-3-5-sonnet-20240620',
            'claude-3-5-sonnet-20241022',
            'claude-3-5-haiku-20241022',
            'claude-3-sonnet-20240229',
            'claude-3-opus-20240229',
            'claude-3-haiku-20240307',
        ]
        
        print("\n🧪 Testing specific models:")
        for model_name in test_models:
            try:
                message = client.messages.create(
                    model=model_name,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                print(f"  ✅ {model_name}: WORKS")
                break
            except Exception as e:
                error_msg = str(e)
                if 'not_found' in error_msg.lower():
                    print(f"  ❌ {model_name}: Not found")
                else:
                    print(f"  ⚠️  {model_name}: {error_msg[:80]}")
except ImportError:
    print("❌ anthropic not installed")
except Exception as e:
    print(f"❌ Error: {e}")

# Test ChatGPT
print("\n" + "=" * 60)
print("🔍 Testing ChatGPT...")
try:
    from openai import OpenAI
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set")
    else:
        print(f"✅ API Key found: {api_key[:10]}...")
        client = OpenAI(api_key=api_key)
        
        # Test model
        try:
            response = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            print(f"  ✅ gpt-4o-mini: WORKS")
        except Exception as e:
            print(f"  ❌ gpt-4o-mini: {e}")
except ImportError:
    print("❌ openai not installed")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Diagnostic complete!")
print("=" * 60)


