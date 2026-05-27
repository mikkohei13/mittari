from flask import Blueprint, render_template

from app.services import observers_taxa

bp = Blueprint("stats", __name__, url_prefix="/stats")


@bp.route("/observers/taxa/<taxon_id>/<int:year>")
@bp.route("/observers/taxa/<taxon_id>", defaults={"year": None})
def observers_taxa_page(taxon_id: str, year: int | None):
    result = observers_taxa.get_observer_taxa_stats(taxon_id=taxon_id, year=year)
    return render_template(
        "stats/observers_taxa.html",
        taxon_id=taxon_id,
        year=year,
        rows=result["rows"],
        total=result.get("total"),
        error=result.get("error"),
    )
