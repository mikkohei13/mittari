"""Business logic: observer species counts under a taxon, from FinBIF warehouse aggregate."""

from __future__ import annotations

from urllib.parse import urlencode

from app.services.finbif_client import FinbifApiError, get_json

_API_BASE = "https://api.laji.fi/warehouse/query/unit/aggregate"

DEFAULT_TAXON_ID = "MX.37600"
DEFAULT_YEAR = 2026


def _taxon_id_param(taxon_id: str) -> str:
    """FinBIF accepts short qnames (e.g. MX.37600) or full taxon URIs."""
    tid = taxon_id.strip()
    if tid.startswith("http://") or tid.startswith("https://"):
        return tid
    return tid


def _fetch_aggregate(*, taxon_id: str, year: int | None) -> dict:
    params = {
        "aggregateBy": "gathering.team.memberName",
        "orderBy": "speciesCount DESC",
        "onlyCount": "true",
        "taxonCounts": "true",
        "gatheringCounts": "false",
        "pairCounts": "false",
        "atlasCounts": "false",
        "excludeNulls": "true",
        "pessimisticDateRangeHandling": "false",
        "pageSize": "100",
        "page": "1",
        "cache": "true",
        "useIdentificationAnnotations": "true",
        "includeSubTaxa": "true",
        "includeNonValidTaxa": "true",
        "individualCountMin": "1",
        "includeNullLoadDates": "false",
        "qualityIssues": "NO_ISSUES",
        "countryId": "ML.206",
        "wild": "WILD,WILD_UNKNOWN",
        "recordQuality": "COMMUNITY_VERIFIED,NEUTRAL,EXPERT_VERIFIED",
        "higherTaxon": "false",
        "taxonId": _taxon_id_param(taxon_id),
    }
    if year is not None:
        params["time"] = str(year)
    url = f"{_API_BASE}?{urlencode(params)}"
    return get_json(url)


def get_observer_taxa_stats(taxon_id: str, year: int) -> dict[str, object]:
    """Return ranked observers for the given taxon and calendar year.

    Returns a dict with ``rows`` (list of ``name`` / ``species_count``),
    optional ``total`` from the API, and optional ``error`` (Finnish message).
    """
    if year < 1500:
        return {
            "rows": [],
            "total": 0,
            "error": "Vuosiluku ei kelpaa.",
        }

    try:
        data = _fetch_aggregate(taxon_id=taxon_id, year=year)
    except FinbifApiError as e:
        return {"rows": [], "total": None, "error": str(e)}

    total = data.get("total", 0)
    results = list(data.get("results", []))

    taxon_counts = [
        r["taxonCount"]
        for r in results
        if isinstance(r.get("taxonCount"), (int, float))
    ]
    if taxon_counts:
        min_taxon = min(taxon_counts)
        filtered = [r for r in results if r.get("speciesCount", 0) >= min_taxon]
    else:
        filtered = results

    rows: list[dict[str, object]] = []
    for item in filtered:
        name = item.get("aggregateBy", {}).get("gathering.team.memberName", "")
        species = item.get("speciesCount", 0)
        if isinstance(species, (int, float)):
            scount = int(species)
        else:
            try:
                scount = int(str(species))
            except ValueError:
                scount = 0
        rows.append({"name": str(name), "species_count": scount})

    total_out: int | None
    if isinstance(total, (int, float)):
        total_out = int(total)
    else:
        total_out = None

    return {
        "rows": rows,
        "total": total_out,
        "error": None,
    }
