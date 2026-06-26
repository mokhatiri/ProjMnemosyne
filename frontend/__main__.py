"""Frontend console CLI.

    python -m frontend                      # serve on http://127.0.0.1:8000
    python -m frontend --port 9000
    python -m frontend --offline            # force the stub reasoner everywhere

Then open the printed URL in a browser. The page talks to the /api/* endpoints,
which proxy into Layers 4-6.
"""

import sys
import argparse
import logging

# Load API tokens from .env if present (so the console picks up HF_TOKEN /
# VOYAGE_API_KEY without exporting them). Optional; shell vars win.
try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from .server import run

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(prog="python -m frontend",
                                     description="ProjMnemosyne web console")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--offline", action="store_true",
                        help="force the offline stub reasoner for all requests")
    args = parser.parse_args()
    run(host=args.host, port=args.port, offline=args.offline)


if __name__ == "__main__":
    main()
