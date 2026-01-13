"""
DSPy Signatures

Defines the AI reasoning signatures for search operations.
Single Responsibility: Only defines what the AI should do.
"""

import dspy


class SearchQA(dspy.Signature):
    """Answer a question using web search context with inline citations."""

    context = dspy.InputField(
        desc="Numbered passages from web search. Each passage is marked [0], [1], [2], etc."
    )
    question = dspy.InputField(desc="The user's question")
    answer = dspy.OutputField(
        desc=(
            "A comprehensive, well-structured answer. REQUIRED FORMAT:\n"
            "1. Use ## headers to organize sections\n"
            "2. Use bullet points (-) for lists of items\n"
            "3. Use numbered lists (1. 2. 3.) for steps or comparisons\n"
            "4. ALWAYS wrap code in triple backticks with language: ```python\n"
            "5. Include [0], [1], [2] citation markers after key claims\n"
            "6. Use **bold** for key terms and concepts\n"
            "Example structure:\n"
            "## Overview\n"
            "Brief intro with citation [0].\n\n"
            "## Key Points\n"
            "- Point one [1]\n"
            "- Point two [2]\n\n"
            "## Code Example\n"
            "```python\ncode here\n```"
        )
    )
    confidence = dspy.OutputField(desc="Confidence score 0-1")


class ContextRanker(dspy.Signature):
    """Select the most relevant passages for a query, considering credibility."""

    query = dspy.InputField(desc="The search query")
    context = dspy.InputField(
        desc="List of passages with indices and credibility scores"
    )
    selected_indices = dspy.OutputField(
        desc=(
            "Comma-separated list of most relevant passage indices. "
            "Prefer high-credibility sources. Example: '1, 3, 5'"
        )
    )


class QueryDecomposer(dspy.Signature):
    """Break complex queries into focused sub-queries for better search coverage."""

    query = dspy.InputField(desc="The user's complex question or comparison request")
    sub_queries = dspy.OutputField(
        desc=(
            "2-4 focused sub-queries separated by newlines. "
            "Each sub-query targets a specific aspect. "
            "Example for 'Compare X and Y':\n"
            "What are the key features of X?\n"
            "What are the key features of Y?\n"
            "X vs Y performance comparison"
        )
    )


class SuggestionGenerator(dspy.Signature):
    """Generate search query suggestions based on context."""

    context = dspy.InputField(
        desc="Trending topics OR user's past search queries (may be empty for new users)"
    )
    user_type = dspy.InputField(
        desc="Either 'new' (no history) or 'returning' (has search history)"
    )
    suggestions = dspy.OutputField(
        desc=(
            "Exactly 5 engaging search query suggestions, one per line. "
            "For NEW users: Use trending topics to suggest interesting tech/science questions. "
            "For RETURNING users: Generate related queries based on their search history. "
            "Make queries specific and curiosity-provoking. "
            "Example:\n"
            "What's new in React 19?\n"
            "How does quantum error correction work?\n"
            "Best practices for microservices architecture\n"
            "AI code assistants comparison 2024\n"
            "WebAssembly use cases in production"
        )
    )
