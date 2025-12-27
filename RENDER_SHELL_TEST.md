# How to Run Diagnostic Test on Render Shell

## Quick Steps

1. **Go to Render Dashboard**
   - Navigate to: `trade-alerts` → **Shell** (in left sidebar)

2. **Open Render Shell**
   - Click "Shell" in the left sidebar
   - You'll see a terminal/console interface

3. **Navigate to Project Root**
   ```bash
   cd ~/project
   ```

4. **Run the Diagnostic Script**
   ```bash
   python test_api_models.py
   ```

5. **Review the Output**
   - ✅ Green checkmarks = Working models
   - ❌ Red X = Failed models
   - 📋 Lists available models

## What the Script Tests

### Gemini
- Lists all available models
- Tests: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-pro`, etc.
- Shows which ones work

### Claude
- Tests: `claude-3-5-sonnet-20241022`, `claude-3-5-sonnet-20240620`, etc.
- Shows which version works

### ChatGPT
- Tests: `gpt-4o-mini`
- Verifies it's working

## Example Output

```
=== API Model Diagnostic Tool ===

🔍 Testing Gemini...
✅ API Key found: AIza...
📋 Listing available Gemini models:
  ✅ models/gemini-1.5-pro
  ✅ models/gemini-1.5-flash
  ...
🧪 Testing specific models:
  ❌ gemini-1.5-flash: 404 error...
  ✅ gemini-1.5-pro: WORKS

🔍 Testing Claude...
✅ API Key found: sk-ant-...
🧪 Testing specific models:
  ❌ claude-3-5-sonnet-20240620: Not found
  ✅ claude-3-5-sonnet-20241022: WORKS

🔍 Testing ChatGPT...
✅ API Key found: sk-proj-...
  ✅ gpt-4o-mini: WORKS
```

## Troubleshooting

### If script not found:
```bash
cd ~/project
ls test_api_models.py  # Check if file exists
```

### If Python not found:
```bash
which python
python3 test_api_models.py  # Try python3 instead
```

### If you see import errors:
The script uses the same packages as your main app, so if it fails, check:
- Are requirements.txt packages installed?
- Are API keys set in Render Environment?

## After Running

1. **Note which models work** (✅ marks)
2. **Update code** if needed with working model names
3. **Share results** if you need help fixing issues

## Alternative: Test Individual Models

You can also test models directly in Python:

```python
# Test Gemini
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); model = genai.GenerativeModel('gemini-1.5-pro'); print(model.generate_content('Hi').text)"

# Test Claude
python -c "from anthropic import Anthropic; client = Anthropic(api_key='YOUR_KEY'); print(client.messages.create(model='claude-3-5-sonnet-20241022', max_tokens=10, messages=[{'role':'user','content':'Hi'}]).content[0].text)"
```


