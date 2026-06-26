"""Thin MCP (Model Context Protocol) server wrapping the Layer 4 tools.

This is the *adapter*: all the logic lives in tools.py (plain functions). Here
we register those functions with a FastMCP server so any MCP client -- Claude
Desktop, the Anthropic Agent SDK, the project's frontend, or `mcp` dev tools --
can discover and call them over the protocol. FastMCP derives each tool's
input schema from the function's type hints and its description from the
docstring, so there's no schema duplication.

`mcp` is imported here (not in tools.py) so the tool functions stay importable
without the SDK installed -- only running the server needs it.

Run it:
    python -m layer4 serve            # stdio transport (what MCP clients spawn)
    python -m layer4 serve --offline  # stub the LLM reasoning tools (no HF_TOKEN)
"""

import logging

from .config import Config
from . import tools

logger = logging.getLogger(__name__)


def build_server(offline: bool = False):
    """Create the FastMCP server with all five tools registered.

    Imported lazily inside the function so importing this module (or tools.py)
    never requires the `mcp` package unless you actually start the server.
    """
    from mcp.server.fastmcp import FastMCP

    config = Config()
    tools.configure(offline=offline)   # decide stub-vs-real reasoner up front

    mcp = FastMCP(config.server_name)
    for fn in tools.TOOLS:
        # FastMCP reads the schema from type hints and the description from the
        # docstring -- the same functions the CLI and Layer 5 import directly.
        mcp.add_tool(fn, name=fn.__name__, description=(fn.__doc__ or "").strip())
    logger.info("MCP server '%s' ready with %d tools: %s",
                config.server_name, len(tools.TOOLS),
                ", ".join(tools.TOOLS_BY_NAME))
    return mcp


def serve(offline: bool = False, transport: str = "stdio") -> None:
    """Build and run the server (blocks, serving over the given transport)."""
    build_server(offline=offline).run(transport=transport)
