"""Minimal FinBIF (api.laji.fi) HTTP client."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class FinbifApiError(Exception):
    """Raised when the FinBIF API returns an error response."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def get_json(url: str, *, timeout: float = 60.0) -> dict:
    """GET a JSON document from api.laji.fi using the warehouse REST headers."""
    token = (os.environ.get("LAJI_API_ACCESS_TOKEN") or "").strip()
    if not token:
        raise FinbifApiError("LAJI_API_ACCESS_TOKEN puuttuu ympäristöstä.")

    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "API-Version": "1",
            "Accept-Language": "fi",
            "Authorization": f"Bearer {token}",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        msg = f"FinBIF API virhe ({e.code})."
        if detail:
            msg = f"{msg} {detail}"
        raise FinbifApiError(msg, status_code=e.code) from e
    except urllib.error.URLError as e:
        raise FinbifApiError(f"Yhteys FinBIF API:in epäonnistui: {e.reason!s}") from e

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise FinbifApiError("FinBIF API palautti virheellisen JSONin.") from e

    if not isinstance(data, dict):
        raise FinbifApiError("FinBIF API palautti odottamattoman vastauksen.")
    return data
