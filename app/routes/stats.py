from flask import Blueprint, render_template

from app.extensions import cache
from app.services import observers_taxa

bp = Blueprint("stats", __name__, url_prefix="/stats")

OBSERVERS_TAXA_CACHE_SECONDS = 20 * 3600


@bp.route("/observers/taxa/<taxon_id>/<int:year>")
@bp.route("/observers/taxa/<taxon_id>", defaults={"year": None})
@cache.cached(timeout=OBSERVERS_TAXA_CACHE_SECONDS)
def observers_taxa_page(taxon_id: str, year: int | None):
    result = observers_taxa.get_observer_taxa_stats(taxon_id=taxon_id, year=year)
    taxon_label = observers_taxa.get_taxon_display_label(taxon_id)
    return render_template(
        "stats/observers_taxa.html",
        taxon_id=taxon_id,
        taxon_label=taxon_label,
        year=year,
        rows=result["rows"],
        total=result.get("total"),
        error=result.get("error"),
    )
