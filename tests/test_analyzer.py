import csv
from pathlib import Path
import pytest
from oprt.analyzer import load_products, write_ranked_csv


def test_sample_data_ranks_and_scores():
    path = Path(__file__).parents[1] / "data" / "sample_products.csv"
    results = load_products(path)
    assert len(results) == 3
    assert results[0].opportunity_score >= results[-1].opportunity_score
    assert 0 <= results[0].opportunity_score <= 100


def test_missing_columns_fails(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("product_name,selling_price\nThing,10\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required columns"):
        load_products(path)


def test_invalid_score_fails(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "product_name,selling_price,cost_price,demand_score,competition_score,trend_score,return_risk\n"
        "Thing,10,5,101,50,50,20\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="between 0 and 100"):
        load_products(path)


def test_report_writer(tmp_path):
    source = Path(__file__).parents[1] / "data" / "sample_products.csv"
    results = load_products(source)
    out = tmp_path / "ranked.csv"
    write_ranked_csv(results, out)
    assert out.exists()
    assert len(list(csv.DictReader(out.open(encoding="utf-8")))) == 3
