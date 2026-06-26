"""Layer 4 (MCP Tool Layer) CLI.

Exposes the research-intelligence tools over the Model Context Protocol, and
lets you invoke any tool directly for testing without an MCP client.

Run from the project root (the folder containing `layer4/`):

    python -m layer4 list                       # show the tools + their schemas
    python -m layer4 serve                       # start the MCP server (stdio)
    python -m layer4 serve --offline             # stub the LLM tools (no HF_TOKEN)
    python -m layer4 call search_papers '{"query":"chain of thought","k":3}'
    python -m layer4 call trace_citations '{"paper_id":"semantic_scholar:1b6e8...","depth":1}'
    python -m layer4 call detect_contradictions '{"topic":"chain of thought"}' --offline

`call` passes the JSON object straight through as keyword arguments to the tool.
The search/related tools work with or without API keys (semantic when a vector
store + key are available, keyword fallback otherwise); the reasoning tools use
the real LLM when HF_TOKEN is set and a clearly-labelled stub under --offline.

(Note: `python -m layer4` works despite... there's no hyphen here, but the tools
reach the hyphenated Layer 3-1/3-2 packages via importlib -- see tools.py.)
"""

import sys
import json
import argparse
import logging

# Load API tokens from a .env file in the project root if present, so secrets
# (HF_TOKEN, VOYAGE_API_KEY, S2_API_KEY) can live there instead of being
# exported in every shell. Shell-set vars take precedence (load_dotenv never
# overrides os.environ); python-dotenv is optional -- if it isn't installed,
# the .env is simply ignored.
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from . import tools

# Same Windows-console fix as the other layers: results contain characters the
# legacy cp1252 codepage can't print.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def cmd_list() -> None:
    """Print each tool name, its one-line purpose, and its parameters."""
    import inspect
    print(f"\n=== {len(tools.TOOLS)} MCP tools ===")
    for fn in tools.TOOLS:
        sig = inspect.signature(fn)
        params = ", ".join(
            p if d.default is inspect.Parameter.empty else f"{p}={d.default!r}"
            for p, d in sig.parameters.items())
        summary = " ".join((fn.__doc__ or "").split())
        print(f"\n{fn.__name__}({params})")
        print(f"  {summary[:300]}")


def cmd_call(name: str, json_args: str, offline: bool) -> None:
    """Invoke one tool with kwargs from a JSON object and print the result."""
    fn = tools.TOOLS_BY_NAME.get(name)
    if fn is None:
        print(f"unknown tool {name!r}. available: "
              f"{', '.join(tools.TOOLS_BY_NAME)}")
        return
    try:
        kwargs = json.loads(json_args) if json_args else {}
    except json.JSONDecodeError as exc:
        print(f"invalid JSON args: {exc}")
        return
    if not isinstance(kwargs, dict):
        print("JSON args must be an object, e.g. '{\"query\": \"...\"}'")
        return
    tools.configure(offline=offline)
    result = fn(**kwargs)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m layer4",
        description="Layer 4 MCP tool layer")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="list tools and their parameters")

    p_serve = sub.add_parser("serve", help="run the MCP server (stdio)")
    p_serve.add_argument("--offline", action="store_true",
                         help="use the stub reasoner for the LLM tools")

    p_call = sub.add_parser("call", help="invoke one tool directly (testing)")
    p_call.add_argument("tool", help="tool name (see `list`)")
    p_call.add_argument("json_args", nargs="?", default="{}",
                        help="JSON object of keyword args")
    p_call.add_argument("--offline", action="store_true",
                        help="use the stub reasoner for the LLM tools")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    if args.command == "list":
        cmd_list()
    elif args.command == "serve":
        from .server import serve   # imports `mcp` only on this path
        serve(offline=args.offline)
    elif args.command == "call":
        cmd_call(args.tool, args.json_args, args.offline)


if __name__ == "__main__":
    main()
