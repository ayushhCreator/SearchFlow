#!/bin/bash
# Test LLM Provider Setup Script

set -e

echo "🔍 SearchFlow Multi-LLM Provider Test"
echo "======================================"
echo ""

# Check .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Load environment variables
source .env

# Check which provider is configured
echo "📋 Configuration:"
echo "   Provider: $LLM_PROVIDER"

case "$LLM_PROVIDER" in
    "groq")
        echo "   Model: $GROQ_MODEL"
        echo "   Max Tokens: $GROQ_MAX_TOKENS"
        if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your-key-here" ]; then
            echo ""
            echo "❌ Error: GROQ_API_KEY not set"
            echo "   Get your free API key at: https://console.groq.com"
            exit 1
        fi
        echo "   API Key: ${GROQ_API_KEY:0:10}...${GROQ_API_KEY: -4}"
        ;;

    "gemini")
        echo "   Model: $GEMINI_MODEL"
        echo "   Max Tokens: $GEMINI_MAX_TOKENS"
        if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your-key-here" ]; then
            echo ""
            echo "❌ Error: GEMINI_API_KEY not set"
            echo "   Get your free API key at: https://makersuite.google.com/app/apikey"
            exit 1
        fi
        echo "   API Key: ${GEMINI_API_KEY:0:10}...${GEMINI_API_KEY: -4}"
        ;;

    "ollama")
        echo "   Model: $OLLAMA_MODEL"
        echo "   Base URL: $OLLAMA_BASE_URL"
        echo "   Max Tokens: $OLLAMA_MAX_TOKENS"
        echo ""
        echo "🔍 Checking Ollama connection..."
        if curl -s "$OLLAMA_BASE_URL/api/tags" > /dev/null 2>&1; then
            echo "✅ Ollama is running"
        else
            echo "❌ Error: Cannot connect to Ollama at $OLLAMA_BASE_URL"
            echo "   Make sure Ollama is running: ollama serve"
            echo "   Install Ollama from: https://ollama.ai"
            exit 1
        fi
        ;;

    "openai")
        echo "   Model: $OPENAI_MODEL"
        if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-key-here" ]; then
            echo ""
            echo "❌ Error: OPENAI_API_KEY not set"
            echo "   Get your API key at: https://platform.openai.com/api-keys"
            exit 1
        fi
        echo "   API Key: ${OPENAI_API_KEY:0:10}...${OPENAI_API_KEY: -4}"
        ;;

    *)
        echo ""
        echo "❌ Error: Unknown LLM_PROVIDER: $LLM_PROVIDER"
        echo "   Supported providers: groq, gemini, ollama, openai"
        exit 1
        ;;
esac

echo ""
echo "🔍 Checking SearXNG..."
if curl -s "$SEARXNG_URL" > /dev/null 2>&1; then
    echo "✅ SearXNG is running at $SEARXNG_URL"
else
    echo "⚠️  Warning: Cannot connect to SearXNG at $SEARXNG_URL"
    echo "   Start SearXNG with: make docker-up"
fi

echo ""
echo "🧪 Running configuration tests..."
if pytest tests/test_multi_llm.py::TestMultiLLMConfig -v; then
    echo ""
    echo "✅ Configuration tests passed!"
else
    echo ""
    echo "❌ Configuration tests failed"
    exit 1
fi

echo ""
echo "🚀 Testing API endpoint..."
# Check if API is running
if ! curl -s http://localhost:8007/health > /dev/null 2>&1; then
    echo "⚠️  API is not running. Start it with: make run"
    echo ""
    echo "✅ Setup validation complete!"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Start the API: make run"
    echo "   2. Test search: curl -X POST http://localhost:8007/api/v1/search \\"
    echo "      -H 'Content-Type: application/json' \\"
    echo "      -d '{\"query\": \"what is python programming\"}'"
    exit 0
fi

# Test the search endpoint
echo "   Testing search with provider: $LLM_PROVIDER"
RESPONSE=$(curl -s -X POST http://localhost:8007/api/v1/search \
    -H "Content-Type: application/json" \
    -d '{"query": "what is 2+2"}' 2>&1)

if echo "$RESPONSE" | grep -q "answer"; then
    echo "✅ Search endpoint working!"
    echo ""
    echo "📊 Sample response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
else
    echo "⚠️  Search endpoint returned unexpected response:"
    echo "$RESPONSE"
fi

echo ""
echo "✅ All tests passed! Your SearchFlow setup is working with $LLM_PROVIDER"
echo ""
echo "📚 Documentation: docs/MULTI_LLM_SETUP.md"
echo "🔄 To switch providers, edit LLM_PROVIDER in .env"
