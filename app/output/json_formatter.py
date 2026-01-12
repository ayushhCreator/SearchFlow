"""
JSON Formatter

Generates structured JSON output from search results.
Single Responsibility: Only handles JSON formatting.
"""

from datetime import datetime
from typing import Any, Dict


class JsonFormatter:
    """Formats search results as structured JSON."""

    @staticmethod
    def format(
        result: Dict[str, Any],
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Format search result as structured JSON.

        Args:
            result: Search result from pipeline
            include_metadata: Include timestamp and version info

        Returns:
            Structured JSON dict
        """
        output = {
            "query": result.get("question", ""),
            "answer": result.get("answer", ""),
            "confidence": result.get("confidence", 0),
            "sources": [],
            "context": [],
        }

        # Format sources
        for url in result.get("sources", []):
            if isinstance(url, str):
                output["sources"].append({"url": url})
            elif isinstance(url, dict):
                output["sources"].append(url)

        # Format context
        for ctx in result.get("context", []):
            if isinstance(ctx, dict):
                output["context"].append(
                    {
                        "text": ctx.get("text", "")[:500],
                        "url": ctx.get("url", ""),
                        "title": ctx.get("title", ""),
                        "source": ctx.get("source", ""),
                    }
                )

        if include_metadata:
            output["metadata"] = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "version": "1.0",
                "cached": result.get("cached", False),
            }

        return output


def format_as_json(result: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for JSON formatting."""
    return JsonFormatter.format(result)
