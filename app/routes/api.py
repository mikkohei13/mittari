"""JSON API routes (proxies to FinBIF where the browser cannot send secrets)."""

from __future__ import annotations

from urllib.parse import urlencode

from flask import Blueprint, jsonify, request

from app.services.finbif_client import FinbifApiError, get_json

bp = Blueprint("api", __name__, url_prefix="/api")

_AUTOCOMPLETE_URL = "https://api.laji.fi/autocomplete/taxa"


@bp.route("/finbif/autocomplete/taxa")
def autocomplete_taxa():
    q = (request.args.get("query") or "").strip()
    if not q:
        return jsonify({"results": []})

    params = {"query": q, "limit": "10", "includeHidden": "false"}
    url = f"{_AUTOCOMPLETE_URL}?{urlencode(params)}"
    try:
        data = get_json(url)
    except FinbifApiError as e:
        return jsonify({"results": [], "error": str(e)}), 502

    return jsonify(data)
