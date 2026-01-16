"""
Greeting Detection

Detects greetings and casual conversation.
"""

GREETING_PATTERNS = [
    "hi", "hello", "hey", "greetings", "good morning", "good afternoon",
    "good evening", "howdy", "what's up", "whats up", "sup", "yo",
    "hola", "bonjour", "namaste", "salut"
]

CASUAL_PATTERNS = [
    "how are you", "how r u", "how do you do", "what's going on",
    "how's it going", "hows it going", "nice to meet you"
]


def is_greeting(query: str) -> bool:
    """Check if query is a greeting or casual conversation."""
    query_lower = query.lower().strip()
    
    # Exact match or starts with greeting
    for pattern in GREETING_PATTERNS + CASUAL_PATTERNS:
        if query_lower == pattern or query_lower.startswith(pattern):
            return True
    
    # Short queries that are likely greetings
    if len(query_lower.split()) <= 3:
        for pattern in GREETING_PATTERNS:
            if pattern in query_lower:
                return True
    
    return False


def get_greeting_response() -> dict:
    """Generate greeting response with suggestions."""
    return {
        "question": "greeting",
        "answer": (
            "## 👋 Hello! I'm SearchFlow\n\n"
            "I search the web and provide **structured, well-researched answers** "
            "with proper citations.\n\n"
            "### What I can help you with:\n"
            "- 🔍 **Research questions** - Get comprehensive answers with sources\n"
            "- 💻 **Technical comparisons** - Compare technologies, frameworks, tools\n"
            "- 📚 **Learning topics** - Understand complex concepts explained simply\n"
            "- 🚀 **Latest updates** - Find current information on any topic\n\n"
            "**Try asking me something below, or pick a suggested question!**"
        ),
        "context": [],
        "confidence": 1.0,
        "sources": [],
        "is_greeting": True
    }
