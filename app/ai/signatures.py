"""
DSPy Signatures

Defines the AI reasoning signatures for search operations.
Single Responsibility: Only defines what the AI should do.
"""

import dspy


class SearchQA(dspy.Signature):
    """Answer a question using web search context."""

    context = dspy.InputField(desc="Information from web search")
    question = dspy.InputField(desc="The user's question")
    answer = dspy.OutputField(desc="A comprehensive answer based on context")
    confidence = dspy.OutputField(desc="Confidence score 0-1")
