"""
MCP Server for SearchFlow

Exposes search functionality as tools for AI agents via MCP protocol.
Compatible with Claude Desktop, GPT-based agents, and other MCP clients.
"""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from app.cache.redis_client import CacheClient, get_cache_client
from app.mcp.search_tool import SearchTools

logger = logging.getLogger(__name__)


def create_mcp_server() -> Server:
    """
    Create and configure MCP server with search tools.

    Returns:
        Configured MCP Server instance
    """
    server = Server("searchflow")
    search_tools: SearchTools | None = None
    cache: CacheClient | None = None

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available search tools."""
        return [
            Tool(
                name="web_search",
                description="Search the web and get an AI-synthesized answer. "
                "Use this for quick questions that need up-to-date information.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query or question to answer",
                        },
                        "skip_cache": {
                            "type": "boolean",
                            "description": "If true, bypass cache and force fresh search",
                            "default": False,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="research_topic",
                description="Deep research on a topic with multiple related queries. "
                "Use this for comprehensive understanding of a subject.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to research in depth",
                        },
                        "depth": {
                            "type": "integer",
                            "description": "Number of related queries (1-5)",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 5,
                        },
                    },
                    "required": ["topic"],
                },
            ),
            Tool(
                name="get_sources",
                description="Get raw search sources without AI synthesis. "
                "Use this to see actual search results.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum sources to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 20,
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a search tool."""
        nonlocal search_tools, cache

        # Initialize tools on first use
        if search_tools is None:
            cache = await get_cache_client()
            search_tools = SearchTools(cache=cache)

        try:
            if name == "web_search":
                result = await search_tools.web_search(
                    query=arguments["query"],
                    skip_cache=arguments.get("skip_cache", False),
                )
                return [
                    TextContent(
                        type="text",
                        text=_format_search_result(result),
                    )
                ]

            elif name == "research_topic":
                result = await search_tools.research_topic(
                    topic=arguments["topic"],
                    depth=arguments.get("depth", 3),
                )
                return [
                    TextContent(
                        type="text",
                        text=_format_research_result(result),
                    )
                ]

            elif name == "get_sources":
                result = await search_tools.get_sources(
                    query=arguments["query"],
                    limit=arguments.get("limit", 10),
                )
                return [
                    TextContent(
                        type="text",
                        text=_format_sources_result(result),
                    )
                ]

            else:
                return [
                    TextContent(
                        type="text",
                        text=f"Unknown tool: {name}",
                    )
                ]

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}",
                )
            ]

    return server


def _format_search_result(result: dict) -> str:
    """Format search result for display."""
    if result.get("error"):
        return f"Error: {result['error']}"

    output = []
    output.append(f"**Answer:**\n{result.get('answer', 'No answer available')}\n")
    output.append(f"**Confidence:** {result.get('confidence', 0):.0%}")

    if result.get("cached"):
        output.append("*(from cache)*")

    sources = result.get("sources", [])
    if sources:
        output.append(f"\n**Sources ({len(sources)}):**")
        for i, url in enumerate(sources[:5], 1):
            output.append(f"  {i}. {url}")

    return "\n".join(output)


def _format_research_result(result: dict) -> str:
    """Format research result for display."""
    output = []
    output.append(f"# Research: {result.get('topic', 'Unknown')}\n")
    output.append(f"*Explored {result.get('queries_explored', 0)} queries*\n")

    for item in result.get("research", []):
        output.append(f"## {item.get('query', '')}")
        output.append(f"{item.get('answer', '')}\n")

    sources = result.get("sources", [])
    if sources:
        output.append(f"## Sources ({len(sources)})")
        for url in sources:
            output.append(f"- {url}")

    return "\n".join(output)


def _format_sources_result(result: dict) -> str:
    """Format sources result for display."""
    if result.get("error"):
        return f"Error: {result['error']}"

    output = []
    output.append(f"**Query:** {result.get('query', '')}")
    output.append(f"**Found:** {result.get('total_found', 0)} sources\n")

    for i, source in enumerate(result.get("sources", []), 1):
        output.append(f"### {i}. {source.get('title', 'Untitled')}")
        output.append(f"**URL:** {source.get('url', '')}")
        output.append(f"**Engine:** {source.get('engine', 'unknown')}")
        output.append(f"{source.get('snippet', '')}\n")

    return "\n".join(output)


async def run_mcp_server():
    """Run the MCP server via stdio."""
    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


def main():
    """Entry point for MCP server."""
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_mcp_server())


if __name__ == "__main__":
    main()
