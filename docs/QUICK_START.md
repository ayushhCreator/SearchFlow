# 🚀 Quick Start - Open Project Checklist

## 1️⃣ First Time Setup (One Time Only)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**Required in `.env`:**

- `GROQ_API_KEY=` (get free at https://console.groq.com)
- OR `GEMINI_API_KEY=` (get free at https://makersuite.google.com/app/apikey)
- OR use `OLLAMA` (local, no API key needed)

---

## 2️⃣ Every Time You Open the Project

### Quick Commands

```bash
# 1. Start all services
make docker-up

# 2. Check services are running
make health

# 3. View logs
make logs

# 4. Test search
curl -X POST http://localhost:8007/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what is python"}'
```

### That's It! ✅

Your SearchFlow is now running:

- 🔍 SearXNG: http://localhost:8888
- 🚀 API: http://localhost:8007
- 📚 Docs: http://localhost:8007/docs

---

## 3️⃣ Common Issues

### Services Not Starting?

```bash
make docker-down
make docker-up
```

### Want to Change LLM Provider?

Edit `.env` and change one line:

```bash
LLM_PROVIDER=groq    # or gemini, ollama, openai
```

Then restart:

```bash
make restart
```

### Check What's Running

```bash
docker-compose ps
```

---

## 📋 All Available Commands

```bash
make docker-up      # Start services
make docker-down    # Stop services
make restart        # Restart API
make logs           # View logs
make health         # Check health
make test           # Run tests
make clean          # Clean cache
```

---

## 🎯 Next Steps

- **Change LLM provider:** Edit `LLM_PROVIDER` in `.env`
- **Full docs:** See [MULTI_LLM_QUICKSTART.md](MULTI_LLM_QUICKSTART.md)
- **Setup guide:** See [SETUP_COMPLETE_MULTI_LLM.md](SETUP_COMPLETE_MULTI_LLM.md)

**Need help?** Run `make help`
