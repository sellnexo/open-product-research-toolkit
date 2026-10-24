"""CSV validation and explainable product-opportunity scoring."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REQUIRED_COLUMNS = {
    "product_name", "selling_price", "cost_price", "demand_score",
    "competition_score", "trend_score", "return_risk",
}
OPTIONAL_COLUMNS = {"evidence_url", "notes"}


@dataclass
class ProductResult:
    product_name: str
    selling_price: float
    cost_price: float
    gross_margin_pct: float
    demand_score: float
    competition_score: float
    trend_score: float
    return_risk: float
    opportunity_score: float
    evidence_url: str = ""
    notes: str = ""
    flags: str = ""


def _number(value: str, field: str, row_num: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Row {row_num}: '{field}' must be a number, got {value!r}.")
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"Row {row_num}: '{field}' must be finite.")
    return number


def load_products(path: str | Path) -> list[ProductResult]:
    """Read and validate a product CSV file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV is empty or has no header row.")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
        results = []
        for row_num, row in enumerate(reader, start=2):
            name = (row.get("product_name") or "").strip()
            if not name:
                raise ValueError(f"Row {row_num}: product_name cannot be blank.")
            selling = _number(row.get("selling_price", ""), "selling_price", row_num)
            cost = _number(row.get("cost_price", ""), "cost_price", row_num)
            if selling <= 0 or cost < 0:
                raise ValueError(f"Row {row_num}: selling_price must be > 0 and cost_price >= 0.")
            values = {}
            for field in ("demand_score", "competition_score", "trend_score", "return_risk"):
                values[field] = _number(row.get(field, ""), field, row_num)
                if not 0 <= values[field] <= 100:
                    raise ValueError(f"Row {row_num}: {field} must be between 0 and 100.")
            margin = (selling - cost) / selling * 100
            # Margin is capped for scoring; a negative margin remains a negative contribution.
            margin_component = max(0.0, min(100.0, margin / 50.0 * 100.0))
            score = (
                values["demand_score"] * 0.30
                + (100 - values["competition_score"]) * 0.20
                + values["trend_score"] * 0.20
                + margin_component * 0.20
                + (100 - values["return_risk"]) * 0.10
            )
            flags = []
            if cost >= selling:
                flags.append("NO_GROSS_PROFIT")
            if not (row.get("evidence_url") or "").strip():
                flags.append("NO_EVIDENCE_URL")
            results.append(ProductResult(
                product_name=name, selling_price=selling, cost_price=cost,
                gross_margin_pct=round(margin, 2),
                demand_score=values["demand_score"],
                competition_score=values["competition_score"],
                trend_score=values["trend_score"],
                return_risk=values["return_risk"],
                opportunity_score=round(score, 2),
                evidence_url=(row.get("evidence_url") or "").strip(),
                notes=(row.get("notes") or "").strip(),
                flags=";".join(flags),
            ))
    if not results:
        raise ValueError("CSV has a header but no product rows.")
    return sorted(results, key=lambda item: item.opportunity_score, reverse=True)


def write_ranked_csv(results: Iterable[ProductResult], path: str | Path) -> None:
    fields = list(ProductResult.__dataclass_fields__.keys())
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)


def write_summary(results: list[ProductResult], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Product Opportunity Summary", "",
        f"Products analyzed: **{len(results)}**", "",
        "> Scores are heuristic research aids, not sales forecasts. Validate every input.", "",
        "| Rank | Product | Opportunity score | Gross margin | Flags |",
        "|---:|---|---:|---:|---|",
    ]
    for rank, item in enumerate(results, start=1):
        safe_name = item.product_name.replace("|", "\\|")
        lines.append(
            f"| {rank} | {safe_name} | {item.opportunity_score:.2f} | "
            f"{item.gross_margin_pct:.2f}% | {item.flags or '—'} |"
        )
    lines += ["", "## Interpretation", "",
              "- Check evidence and data freshness before acting.",
              "- Compare shipping, marketplace fees, taxes, advertising, packaging, and return costs separately.",
              "- Negative or thin margins need attention even if demand signals look strong.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
