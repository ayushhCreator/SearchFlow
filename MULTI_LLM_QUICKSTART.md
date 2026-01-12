# 🎯 Multi-LLM Quick Reference

## One-Line Provider Switch

```bash
# In .env, change this ONE line:
LLM_PROVIDER=groq     # ← Change this to: groq, gemini, or ollama
```

## Available Providers

| Provider   | In .env               | Speed             | Cost | API Key Required     |
| ---------- | --------------------- | ----------------- | ---- | -------------------- |
| **Groq**   | `LLM_PROVIDER=groq`   | ⚡⚡⚡ Ultra Fast | Free | ✅ Yes (already set) |
| **Gemini** | `LLM_PROVIDER=gemini` | ⚡⚡ Fast         | Free | ✅ Yes (already set) |
| **Ollama** | `LLM_PROVIDER=ollama` | ⚡ Slow           | Free | ❌ No (local)        |
| OpenAI     | `LLM_PROVIDER=openai` | ⚡⚡ Fast         | Paid | ✅ Yes (not set)     |

## Quick Test Commands

```bash
# 1. Check current config
grep "LLM_PROVIDER" .env

# 2. Test with example
python3 example_multi_llm.py

# 3. Test via API
curl -X POST http://localhost:8007/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what is 2+2"}'
```

## Current Status

```
✅ Provider: groq
✅ Model: llama-3.1-8b-instant
✅ Groq API Key: Configured
✅ Gemini API Key: Configured
✅ Ready to use!
```

## Switch Provider (3 Ways)

**Method 1: Edit .env file directly**

```bash
nano .env
# Change: LLM_PROVIDER=groq
# To: LLM_PROVIDER=gemini
```

**Method 2: Use sed command**

```bash
# Switch to Gemini
sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=gemini/' .env

# Switch to Ollama
sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env

# Switch back to Groq
sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=groq/' .env
```

**Method 3: Use environment variable**

```bash
# Temporarily override (just for this command)
LLM_PROVIDER=gemini python3 example_multi_llm.py
```

## Ollama Setup (If You Want Local)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Pull a model
ollama pull llama2

# 3. Start Ollama server
ollama serve

# 4. Switch to Ollama
sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env

# 5. Test
python3 example_multi_llm.py
```

## Files You Need to Know

- **[.env](.env)** - Change `LLM_PROVIDER` here
- **[docs/MULTI_LLM_SETUP.md](docs/MULTI_LLM_SETUP.md)** - Full documentation
- **[SETUP_COMPLETE_MULTI_LLM.md](SETUP_COMPLETE_MULTI_LLM.md)** - What was configured

## That's It! 🎉

No code changes needed. Just change `LLM_PROVIDER` in `.env` and restart!
