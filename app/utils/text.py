"""
Text Utility Functions

This module provides helper functions for text processing.
"""


def clean_text(text: str) -> str:
    """Remove extra whitespace and normalize text"""
    return " ".join(text.split())


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
