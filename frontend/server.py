"""A tiny HTTP console over the whole stack -- stdlib only, no web framework.

Keeping with the project's minimal-deps stance, this uses Python's built-in
``http.server`` rather than FastAPI/Flask. It serves one static page and a
handful of JSON endpoints that proxy straight into the layers we built:

    GET /                       -> the single-page console (static/index.html)
    GET /api/search?q=&k=       -> Layer 4 search_papers
    GET /api/related?paper_id=  -> Layer 4 find_related_work
    GET /api/citations?paper_id=&depth=  -> Layer 4 trace_citations
    GET /api/agent?name=&topic= -> Layer 5 run_agent (one analytical agent)
    GET /api/investigate?topic= -> Layer 6 Coordinator (A2A: all agents + cross-validate)
    GET /api/explain-insight?id= -> LLM explainer for a banked insight
    GET /api/analyst/status     -> autonomous analyst: live progress + wait countdown
    GET /api/analyst/config     -> autonomous analyst: current runtime config
    POST /api/analyst/start|pause|resume|stop|run-now|reset -> lifecycle controls
    POST /api/analyst/config    -> retune pace / sources / per-source queries
    GET /api/health             -> liveness + which layers imported

Everything degrades gracefully without API keys (Layer 4 falls back to keyword
search; the reasoning paths fall back to the offline stub), so the console is
usable offline. Pass --offline (CLI) to force the stub everywhere.

This is a single-threaded server on purpose: the lower layers keep module-level
singletons (loaded store, configured reasoner) that aren't built for concurrent
mutation. It's a local demo console, not a production service.
"""

import json
import logging
import os
from copy import deepcopy
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from .supervisor import supervisor, WORK_LOCK

logger = logging.getLogger(__name__)

_DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")
# the autonomous analyst writes ranked insights here (project-root/storage)
_INSIGHTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "storage", "insights.jsonl")

_EXPLAIN_SYSTEM = """\
You explain AI research-paper insights to beginners.

You are given one stored insight from a research-intelligence system. Explain
the underlying subject as if the reader knows nothing about the paper or the
technology. Stay grounded in the supplied insight data. Do not invent paper
results, benchmarks, or claims that are not present.

Respond with JSON only, no prose outside JSON, matching exactly:
{"subject": "<what the technology/topic is in simple terms>",
 "why_it_matters": "<why researchers or builders care about it>",
 "insight": "<what this specific insight says in plain language>",
 "supporting": "<what evidence or reasoning supports this insight>",
 "evidence": "<how the supplied claims/details support or qualify it>",
 "contradicting": "<what evidence or reasoning contradicts this insight>",
 "caveats": "<what not to over-read from this insight>",
 "full_details": "<the full insight details, in plain language, for context>",
 "technical_terms": "<any technical terms or jargon in the insight, explained simply>"
 }
"""


def _to_jsonable(obj):
    """Make a response JSON-safe. Findings/Reports are dataclasses; they can
    arrive bare, in a list, or nested inside a dict (e.g. the /api/agent
    payload {"findings": [Finding, ...]}), so recurse through dicts and lists."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(x) for x in obj]
    return obj


def _compact_insight(insight: dict) -> dict:
    """Keep the LLM prompt focused and bounded while preserving useful context."""
    data = deepcopy(insight)
    details = data.get("details")
    if not isinstance(details, dict):
        return data
    for key in ("supporting", "contradicting"):
        if isinstance(details.get(key), list):
            details[key] = details[key][:5]
    for key in ("grounded_in",):
        if isinstance(details.get(key), list):
            details[key] = details[key][:5]
    return data


def _load_insights() -> list:
    insights = []
    if os.path.exists(_INSIGHTS_PATH):
        with open(_INSIGHTS_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        insights.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return insights


def _read_jsonl_latest(path, id_of) -> dict:
    """Append-only JSONL -> {id: latest record} (the project-wide pattern)."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                out[id_of(rec)] = rec
    return out


class ConsoleHandler(BaseHTTPRequestHandler):
    """Routes the handful of GET endpoints. ``offline`` is set on the class by
    run() before serving."""

    offline = False

    # quieter logging than the default one-line-per-request to stderr
    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)

    # --- helpers ---------------------------------------------------------------
    def _send_json(self, obj, status=200):
        body = json.dumps(_to_jsonable(obj), ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        try:
            with open(path, "rb") as fh:
                body = fh.read()
        except FileNotFoundError:
            self._send_json({"error": f"not found: {os.path.basename(path)}"}, 404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _one(params, key, default=None):
        vals = params.get(key)
        return vals[0] if vals else default

    def _read_json_body(self):
        """Parse the request body as JSON ({} when empty). Tolerant of no body."""
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw.strip():
            return {}
        return json.loads(raw.decode("utf-8"))

    def _want_offline(self, params) -> bool:
        # server-wide --offline, OR a per-request ?offline=1
        return self.offline or self._one(params, "offline") in ("1", "true", "yes")

    # --- routing ---------------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path, params = parsed.path, parse_qs(parsed.query)
        try:
            if path in ("/", "/index.html"):
                return self._send_file(os.path.join(_DIST_DIR, "index.html"),
                                       "text/html; charset=utf-8")
            
            # Serve Vite-generated JS/CSS
            if path.startswith("/assets/"):
                asset = os.path.join(
                    _DIST_DIR,
                    path.lstrip("/")
                )

                if path.endswith(".js"):
                    return self._send_file(
                        asset,
                        "application/javascript"
                    )

                if path.endswith(".css"):
                    return self._send_file(
                        asset,
                        "text/css"
                    )

                return self._send_json(
                    {"error": "asset not found"},
                    404
                )


            if path == "/api/health":
                return self._route_health()
            if path == "/api/search":
                return self._route_search(params)
            if path == "/api/related":
                return self._route_related(params)
            if path == "/api/citations":
                return self._route_citations(params)
            if path == "/api/agent":
                return self._route_agent(params)
            if path == "/api/investigate":
                return self._route_investigate(params)
            if path == "/api/insights":
                return self._route_insights(params)
            if path == "/api/explain-insight":
                return self._route_explain_insight(params)
            if path == "/api/overview":
                return self._route_overview()
            if path == "/api/corpus":
                return self._route_corpus()
            if path == "/api/analyst/status":
                return self._send_json(supervisor.status())
            if path == "/api/analyst/config":
                from analyst import runtime_config
                return self._send_json({"config": runtime_config.load(),
                                        "all_sources": runtime_config.ALL_SOURCES,
                                        "default_queries": runtime_config.DEFAULT_QUERIES})
            self._send_json({"error": f"unknown path {path}"}, 404)
        except Exception as exc:                       # never 500 silently
            logger.exception("request failed: %s", self.path)
            self._send_json({"error": f"{type(exc).__name__}: {exc}"}, 500)

    def do_POST(self):
        """State-changing analyst controls. Body (if any) is JSON."""
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = self._read_json_body()
            actions = {
                "/api/analyst/start": lambda: supervisor.start(),
                "/api/analyst/pause": lambda: supervisor.pause(),
                "/api/analyst/resume": lambda: supervisor.resume(),
                "/api/analyst/stop": lambda: supervisor.stop(),
                "/api/analyst/run-now": lambda: supervisor.run_now(),
                "/api/analyst/reset": lambda: supervisor.reset(),
                "/api/analyst/config": lambda: supervisor.update_config(body or {}),
            }
            handler = actions.get(path)
            if handler is None:
                return self._send_json({"error": f"unknown path {path}"}, 404)
            result = handler()
            return self._send_json(result, 200 if result.get("ok") else 400)
        except Exception as exc:
            logger.exception("POST failed: %s", self.path)
            self._send_json({"error": f"{type(exc).__name__}: {exc}"}, 500)

    # --- endpoint implementations ---------------------------------------------
    def _route_health(self):
        import layer4.tools  # noqa: F401  (import = liveness check)
        self._send_json({"status": "ok", "offline_default": self.offline,
                         "endpoints": ["/api/search", "/api/related",
                                       "/api/citations", "/api/agent",
                                       "/api/investigate", "/api/insights",
                                       "/api/explain-insight", "/api/overview",
                                       "/api/corpus", "/api/analyst/status",
                                       "/api/analyst/config"]})

    def _route_search(self, params):
        import layer4.tools as tools
        q = self._one(params, "q")
        if not q:
            return self._send_json({"error": "missing ?q="}, 400)
        k = int(self._one(params, "k", 10))
        year = self._one(params, "year")
        category = self._one(params, "category")
        self._send_json(tools.search_papers(
            q, k=k, year=int(year) if year else None, category=category))

    def _route_related(self, params):
        import layer4.tools as tools
        pid = self._one(params, "paper_id")
        if not pid:
            return self._send_json({"error": "missing ?paper_id="}, 400)
        self._send_json(tools.find_related_work(pid, k=int(self._one(params, "k", 10))))

    def _route_citations(self, params):
        import layer4.tools as tools
        pid = self._one(params, "paper_id")
        if not pid:
            return self._send_json({"error": "missing ?paper_id="}, 400)
        self._send_json(tools.trace_citations(pid, depth=int(self._one(params, "depth", 2))))

    def _route_agent(self, params):
        import layer5
        name = self._one(params, "name")
        if name not in layer5.AGENTS:
            return self._send_json(
                {"error": f"unknown agent; choose from {list(layer5.AGENTS)}"}, 400)
        topic = self._one(params, "topic")
        k = self._one(params, "k")
        # serialize with a possibly-running analyst generation (shared reasoner/store)
        with WORK_LOCK:
            findings = layer5.run_agent(name, topic=topic, k=int(k) if k else None,
                                        offline=self._want_offline(params))
        self._send_json({"agent": name, "topic": topic, "count": len(findings),
                         "findings": findings})

    def _route_investigate(self, params):
        import layer6
        topic = self._one(params, "topic")
        if not topic:
            return self._send_json({"error": "missing ?topic="}, 400)
        k = self._one(params, "k")
        with WORK_LOCK:
            report = layer6.Coordinator(offline=self._want_offline(params)).investigate(
                topic, k=int(k) if k else None)
        self._send_json(report)

    def _route_overview(self):
        """Dashboard snapshot: corpus/graph size, insight distribution, and the
        live analyst status -- everything the Overview view needs in one call.
        Degrades gracefully if the graph isn't built yet."""
        import importlib
        # --- knowledge graph counts (guarded; graph may not be built) ---
        graph = {"built": False, "nodes": {}, "edges": {}}
        try:
            store = importlib.import_module("layer3-2.queries").load()
            graph = {"built": True,
                     "nodes": store.nodes_by_type_counts(),
                     "edges": store.edges_by_type()}
        except FileNotFoundError:
            pass
        except Exception as exc:
            logger.warning("overview: graph load failed (%s)", exc)

        # --- insight distribution ---
        insights = _load_insights()
        by_kind, by_conf = {}, {}
        stub = 0
        for d in insights:
            by_kind[d.get("kind", "?")] = by_kind.get(d.get("kind", "?"), 0) + 1
            by_conf[d.get("confidence", "?")] = by_conf.get(d.get("confidence", "?"), 0) + 1
            if d.get("stub"):
                stub += 1
        insights.sort(key=lambda d: d.get("_score", 0), reverse=True)

        npaper = graph["nodes"].get("Paper", 0)
        self._send_json({
            "corpus": {
                "papers": npaper,
                "papers_cited_external": graph["nodes"].get("Paper(stub)", 0),
                "methods": graph["nodes"].get("Method", 0),
                "claims": graph["nodes"].get("Claim", 0),
                "datasets": graph["nodes"].get("Dataset", 0),
                "authors": graph["nodes"].get("Author", 0),
                "graph_built": graph["built"],
                "edges_total": sum(graph["edges"].values()),
            },
            "graph": graph,
            "insights": {
                "total": len(insights),
                "by_kind": by_kind,
                "by_confidence": by_conf,
                "stub": stub,
                "real": len(insights) - stub,
                "top": insights[:5],
            },
            "analyst": supervisor.status(),
        })

    def _route_corpus(self):
        """What's already digested -- so the query views can show a browseable
        catalog instead of an empty box. Papers come from Layer 1's metadata
        (deduped, latest), methods/datasets from the Layer 3-2 graph."""
        import importlib
        from layer4.config import Config as L4Config
        cfg = L4Config()

        papers_raw = _read_jsonl_latest(
            cfg.metadata_path, lambda r: f"{r.get('source')}:{r.get('source_id')}")
        extracted = set(_read_jsonl_latest(cfg.extracted_path,
                                           lambda r: r["paper_id"]))
        papers = []
        for pid, r in papers_raw.items():
            pub = (r.get("published") or "")[:4]
            papers.append({
                "paper_id": pid,
                "title": r.get("title"),
                "year": int(pub) if pub.isdigit() else None,
                "categories": r.get("categories") or [],
                "authors": (r.get("authors") or [])[:4],
                "snippet": (r.get("abstract") or "")[:220],
                "extracted": pid in extracted,   # fully digested into the graph
            })
        # fully-digested first, then newest, then title
        papers.sort(key=lambda p: (not p["extracted"], -(p["year"] or 0),
                                   (p["title"] or "").lower()))

        methods, datasets = [], []
        try:
            g = importlib.import_module("layer3-2.queries").load().g
            for nid, d in g.nodes(data=True):
                if d.get("type") == "Method":
                    n = sum(1 for *_, e in g.in_edges(nid, data=True)
                            if e.get("type") in ("INTRODUCES", "USES"))
                    methods.append({"label": d.get("label"), "papers": n})
                elif d.get("type") == "Dataset":
                    datasets.append({"label": d.get("label")})
            methods.sort(key=lambda m: (-m["papers"], (m["label"] or "").lower()))
            datasets.sort(key=lambda x: (x["label"] or "").lower())
        except FileNotFoundError:
            pass

        self._send_json({
            "papers": papers,
            "methods": methods,
            "datasets": datasets,
            "counts": {"papers": len(papers), "extracted": len(extracted),
                       "methods": len(methods), "datasets": len(datasets)},
        })

    def _route_insights(self, params):
        """Ranked insights banked by the autonomous analyst (read-only view).
        Returns [] if the analyst hasn't run yet."""
        top = int(self._one(params, "top", 25))
        insights = _load_insights()
        insights.sort(key=lambda d: d.get("_score", 0), reverse=True)
        self._send_json({"count": len(insights), "insights": insights[:top]})

    def _route_explain_insight(self, params):
        """Ask the configured LLM to explain a stored insight for a beginner."""
        if self._want_offline(params):
            return self._send_json(
                {"error": "LLM explanations are disabled in offline mode."}, 503)
        insight_id = self._one(params, "id")
        if not insight_id:
            return self._send_json({"error": "missing ?id="}, 400)
        insight = next((d for d in _load_insights() if d.get("id") == insight_id), None)
        if not insight:
            return self._send_json({"error": f"unknown insight id {insight_id}"}, 404)

        from layer4.config import Config
        from layer4.reasoner import HFReasoner

        try:
            reasoner = HFReasoner(Config())
        except RuntimeError as exc:
            return self._send_json({"error": str(exc).splitlines()[0]}, 503)

        prompt = (
            "Insight JSON:\n"
            f"{json.dumps(_compact_insight(insight), ensure_ascii=False, indent=2)}"
        )
        explanation = reasoner._complete_json(_EXPLAIN_SYSTEM, prompt)
        if not explanation:
            return self._send_json({"error": "LLM returned no usable explanation"}, 502)
        self._send_json({
            "id": insight_id,
            "model": reasoner.model_name,
            "explanation": explanation,
        })


def run(host: str = "127.0.0.1", port: int = 8000, offline: bool = False) -> None:
    """Start the console server (blocks)."""
    ConsoleHandler.offline = offline
    supervisor._offline_default = offline   # status() cold-reads honour --offline
    httpd = HTTPServer((host, port), ConsoleHandler)
    mode = "offline stub" if offline else "auto (real keys if present, else degrade)"
    print(f"ProjMnemosyne console -> http://{host}:{port}   (reasoning: {mode})")
    print("Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
        httpd.server_close()
