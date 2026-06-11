"""
IAMShield - AI Analysis Route
POST /api/ai/analyse
"""
from flask import Blueprint, request, Response, stream_with_context, jsonify
from dotenv import load_dotenv
import os, json, urllib.request, urllib.error

load_dotenv()
ai_bp = Blueprint("ai", __name__)
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

@ai_bp.route("/ai/analyse", methods=["POST", "OPTIONS"])
def ai_analyse():
    if request.method == "OPTIONS":
        r = Response("", status=204)
        r.headers["Access-Control-Allow-Origin"]  = "*"
        r.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        r.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return r

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key or api_key == "your_anthropic_api_key_here":
        return jsonify({"error": "ANTHROPIC_API_KEY not set in backend/.env"}), 500

    data   = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    payload = json.dumps({
        "model":      "claude-sonnet-4-20250514",
        "max_tokens": 400,
        "stream":     True,
        "messages":   [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    def generate():
        req = urllib.request.Request(
            ANTHROPIC_API_URL,
            data=payload,
            headers={
                "Content-Type":      "application/json",
                "x-api-key":         api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                for raw_line in resp:
                    yield raw_line.decode("utf-8").rstrip("\n") + "\n"
        except urllib.error.HTTPError as e:
            yield f"data: {json.dumps({'error': e.read().decode()})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        }
    )