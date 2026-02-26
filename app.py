"""
app.py — Flask web server for the PRD Generator.

Routes:
  GET  /          → Serve the main UI
  POST /generate  → Stream a PRD via Server-Sent Events (SSE)
  GET  /health    → Health check

Usage:
  python app.py
  # then open http://localhost:5000
"""

import json
import os
import sys

from flask import Flask, Response, jsonify, render_template, request, stream_with_context

from prd_generator import PRDGenerator

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _get_api_key() -> str | None:
    """Return the Anthropic API key from config.json or environment."""
    if os.path.exists("config.json"):
        try:
            with open("config.json") as f:
                cfg = json.load(f)
            key = cfg.get("api_key", "").strip()
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass
    return os.environ.get("ANTHROPIC_API_KEY")


def _get_model() -> str:
    if os.path.exists("config.json"):
        try:
            with open("config.json") as f:
                return json.load(f).get("model", "claude-sonnet-4-6")
        except Exception:
            pass
    return os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Stream PRD generation via Server-Sent Events."""
    api_key = _get_api_key()
    if not api_key:
        return jsonify({
            "error": (
                "Anthropic API key not found. "
                "Add it to config.json as \"api_key\" or set the "
                "ANTHROPIC_API_KEY environment variable."
            )
        }), 400

    data = request.get_json(force=True) or {}

    # Validate required fields
    required = ["product_name", "problem_statement", "target_users", "proposed_solution"]
    missing = [f for f in required if not data.get(f, "").strip()]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 422

    format_type = data.get("format_type", "standard")
    model = data.get("model") or _get_model()

    def sse_stream():
        try:
            generator = PRDGenerator(api_key=api_key, model=model)
            for chunk in generator.generate_stream(data, format_type):
                payload = json.dumps({"text": chunk})
                yield f"data: {payload}\n\n"
        except Exception as exc:  # noqa: BLE001
            error_payload = json.dumps({"error": str(exc)})
            yield f"data: {error_payload}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(sse_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok", "model": _get_model()})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = "--debug" in sys.argv or os.environ.get("FLASK_DEBUG", "0") == "1"

    api_key = _get_api_key()
    if not api_key:
        print(
            "\n⚠  Warning: No Anthropic API key found.\n"
            "   Copy config.example.json → config.json and add your key,\n"
            "   or set the ANTHROPIC_API_KEY environment variable.\n"
        )

    print(f"\n🚀  PRD Generator running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
