# Open Product Research Toolkit (OPRT)

A small, transparent, open-source toolkit for exploring product-opportunity data from CSV files.

**What it does**
- Validates product research CSV files.
- Calculates explainable opportunity scores from demand, competition, margin, trend, and return-risk signals.
- Flags missing or suspicious data instead of silently guessing.
- Exports a ranked CSV report and a readable Markdown summary.
- Includes synthetic sample data, tests, and GitHub contribution templates.

**What it does not do**
- It does not scrape marketplaces or bypass platform rules.
- It does not claim that a score guarantees sales.
- It does not fetch live trends or verify marketplace demand. Supply your own data and evidence.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

python -m pip install -e .
oprt validate data/sample_products.csv
oprt analyze data/sample_products.csv --out reports
```

Output files:
- `reports/ranked_products.csv`
- `reports/summary.md`

## Input CSV columns

Required columns:

| Column | Meaning | Expected range |
|---|---|---|
| `product_name` | Product name | Non-empty text |
| `selling_price` | Expected selling price | > 0 |
| `cost_price` | Purchase/landed cost | >= 0 |
| `demand_score` | Evidence-based demand estimate | 0–100 |
| `competition_score` | Competition intensity (higher = more competition) | 0–100 |
| `trend_score` | Trend evidence strength | 0–100 |
| `return_risk` | Estimated return risk | 0–100 |

Optional: `evidence_url`, `notes`.

Scores are only as reliable as the evidence entered. Document sources and dates in `notes` or `evidence_url`.

## Scoring model

The toolkit computes:
- Gross margin percentage = `(selling_price - cost_price) / selling_price * 100`
- Demand contribution: 30%
- Competition advantage: 20% (`100 - competition_score`)
- Trend contribution: 20%
- Margin contribution: 20%, normalized to 0–100 against a 50% reference margin
- Return-risk contribution: 10% (`100 - return_risk`)

The final score is a weighted heuristic, not a prediction. Change weights only with a documented rationale and validate them against real outcomes before relying on them.

## Responsible use

- Respect the terms and access rules of data sources.
- Do not enter personal data, credentials, or confidential supplier/customer information.
- Verify prices, shipping, tax, fees, and return costs independently.
- A high score is a lead for further research, not a buy recommendation.

## Project status

Early-stage project. It currently uses synthetic example data. Contributions, real-world validation, accessibility improvements, and additional input formats are welcome.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## Roadmap
- [ ] Add configurable scoring weights
- [ ] Add a simple browser-based report
- [ ] Add validation for additional currencies
- [ ] Test score usefulness against anonymized real outcomes
- [ ] Add source-date and confidence fields

## License
MIT. See `LICENSE`.
