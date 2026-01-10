# ⚡ Quick Reference Guide

**Fast lookup for commands and concepts - bookmark this!**

---

## 🚀 Start Here

```bash
# Read documentation first
# Then follow Step 1: docs/4.step1_directory_and_files.md

# Basic setup flow:
Step 1: mkdir all directories        # 30 min
Step 2: uv venv & pip install       # 30 min
Step 3: docker build                 # 1 hour
Step 4: GitHub Actions workflows     # 1 hour
Step 5: FastAPI implementation       # 1-2 hours
```

---

## 📁 Step 1: Directory Creation

```bash
# Create directories
mkdir -p app/{api,mcp,search,ai,schemas,core,utils}
mkdir -p tests docker

# Create __init__.py in all packages
touch app/__init__.py app/{api,mcp,search,ai,schemas,core,utils}/__init__.py
touch tests/__init__.py

# Create main files
touch app/main.py app/api/search.py app/core/{config.py,logging.py}
```

---

## 🐍 Step 2: Environment Setup

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev,test]"

# Verify
python -c "import fastapi; print(fastapi.__version__)"
```

---

## 🐳 Step 3: Docker

```bash
# Install Docker
# Ubuntu: sudo apt-get install docker.io docker-compose
# macOS: brew install docker docker-compose
# Windows: Download Docker Desktop

# Build image
docker build -f docker/Dockerfile.api -t searchflow:latest .

# Run container
docker run -p 8007:8007 searchflow:latest

# Docker Compose (all services)
docker-compose up

# Docker Compose (background)
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api
```

---

## 🔄 Step 4: GitHub Actions

```yaml
# Create workflow: .github/workflows/ci.yml
# Key sections:
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

---

## 🌐 Step 5: FastAPI

```python
# Basic endpoint
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class SearchRequest(BaseModel):
    query: str

@app.post("/api/v1/search")
async def search(request: SearchRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query required")

    return {
        "query": request.query,
        "results": [],
        "status": "success"
    }

# Run locally
# python app/main.py
# Visit http://localhost:8007/docs
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_health.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_health.py::test_root_endpoint

# Run only unit tests
pytest -m unit
```

---

## 📋 Common Commands

```bash
# Git
git add .
git commit -m "message"
git push origin main

# Python
python -m venv .venv
source .venv/bin/activate
pip freeze > requirements.txt
python -m pytest

# Docker
docker ps                  # List running
docker images              # List images
docker logs <id>          # View logs
docker exec -it <id> bash # Shell into container

# uv
uv pip list
uv pip install package
uv pip install -e ".[dev]"
uv venv .venv
```

---

## 🔧 File Checklist

```
✓ app/__init__.py
✓ app/main.py
✓ app/api/search.py
✓ app/core/config.py
✓ app/core/logging.py
✓ tests/test_health.py
✓ docker/Dockerfile.api
✓ docker-compose.yml
✓ pyproject.toml
✓ requirements.txt
✓ .env.example
✓ .gitignore
✓ .github/workflows/ci.yml
```

---

## 🐛 Troubleshooting Quick Fixes

| Problem               | Solution                                                |
| --------------------- | ------------------------------------------------------- |
| "python not found"    | Check PATH, reinstall Python                            |
| ".venv not activated" | Run `source .venv/bin/activate`                         |
| "ModuleNotFoundError" | Install requirements: `pip install -r requirements.txt` |
| "Port 8007 in use"    | Kill process: `lsof -i :8007 \| kill -9 <PID>`          |
| "Docker not found"    | Install Docker, add to PATH                             |
| "Permission denied"   | Use `sudo`, or add user to docker group                 |
| "Build fails"         | Check Dockerfile path, run from root                    |

---

## 📊 Step Complexity

```
Step 1: ⭐ EASY           (1-2 hours)
Step 2: ⭐⭐ BEGINNER       (1-2 hours)
Step 3: ⭐⭐⭐ INTERMEDIATE  (2-3 hours)
Step 4: ⭐⭐⭐ INTERMEDIATE  (2-3 hours)
Step 5: ⭐⭐⭐⭐ ADVANCED    (3-4 hours)

Total: 9-14 hours
```

---

## 🔗 Key Ports

```
8007 - FastAPI application
8888 - SearXNG search engine
5432 - PostgreSQL (if added)
6379 - Redis (if added)
```

---

## 🎯 Verification Commands

```bash
# Python version
python --version          # Should be 3.12+

# Package installation
pip list | grep fastapi   # Check FastAPI installed

# Docker
docker --version
docker run hello-world    # Test Docker works

# API health
curl http://localhost:8007/health

# Tests pass
pytest --tb=short
```

---

## 📚 Documentation Files

```
0.master_index.md              ← Start here!
1.project_explained.md         ← What is SearchFlow?
2.tech_stack.md                ← Why each technology?
3.project_structure.md         ← Project layout
4.step1_directory_and_files.md ← CREATE STRUCTURE
5.step2_uv_setup.md            ← INSTALL DEPS
6.step3_docker_setup.md        ← BUILD CONTAINERS
7.step4_cicd_basics.md         ← AUTOMATE
8.step5_fastapi_implementation.md ← BUILD API
```

---

## ⚙️ Environment Variables

```bash
# .env file
DEBUG=false
LOG_LEVEL=INFO
SEARXNG_URL=http://localhost:8888
ALLOWED_ORIGINS=http://localhost,http://localhost:8007
```

---

## 📦 Dependencies Summary

```
Core:
  - fastapi >= 0.104.0
  - uvicorn >= 0.24.0
  - pydantic >= 2.0.0
  - httpx >= 0.25.0

Dev:
  - pytest >= 7.4.0
  - black >= 23.0.0
  - ruff >= 0.1.0
  - mypy >= 1.7.0
```

---

## 🚨 Important Notes

1. **Always activate venv first**

   ```bash
   source .venv/bin/activate
   ```

2. **Always use requirements.txt for Docker**

   ```bash
   pip freeze > requirements.txt
   ```

3. **Always commit lock file**

   ```bash
   git add uv.lock
   ```

4. **Never commit .env**

   ```bash
   # .env should be in .gitignore
   ```

5. **Always verify before pushing**
   ```bash
   pytest
   docker-compose up
   ```

---

## 💻 Text Editors

**Recommended: VS Code**

- Extensions: Python, Docker, GitHub Actions
- Settings: Format on save, linting enabled

---

## 🎓 Learning Tips

1. **Read before executing** - Understand what each command does
2. **Run commands one by one** - Don't copy-paste long blocks
3. **Check outputs** - Verify each step worked
4. **Read errors carefully** - They tell you what's wrong
5. **Take notes** - Write down what you learn
6. **Experiment** - Try modifying code after following guide

---

## ✨ You're Ready!

Save this reference guide for quick lookups.

**Next step:** Go to `docs/0.master_index.md` or directly to `docs/4.step1_directory_and_files.md`

---

_Quick Reference v0.1_
_For SearchFlow Setup Guide_
_Bookmark this page!_
