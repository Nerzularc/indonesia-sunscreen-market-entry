import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))

import market_model as mm  # noqa: E402


def test_population_inputs_match_bps_table():
    # BPS 2025 projection (thousands): women 15-19..30-34 and men 15-19..30-34
    assert round(10706.3 + 10760.0 + 10981.9 + 10870.5, 1) / 1000 == mm.A["women_15_34_m"]["value"]
    assert round(11389.4 + 11400.7 + 11532.3 + 11323.8, 1) / 1000 == mm.A["men_15_34_m"]["value"]


def test_funnel_is_monotonic_and_consistent():
    r = mm.run()
    assert r["tam_idr_bn"] > r["sam_idr_bn"] > r["som_idr_bn"]["high"] > r["som_idr_bn"]["base"] > r["som_idr_bn"]["low"]
    assert abs(r["tam_idr_bn"] - (r["bottom_up"]["tam_idr_bn"] + r["top_down"]["tam_idr_bn"]) / 2) < 1e-6


def test_tam_is_plausible_share_of_skincare_market():
    r = mm.run()
    share = r["tam_usd_m"] / 3070  # US$3.07B skin care market (Ken Research / Inkwood)
    assert 0.03 < share < 0.25


def test_sensitivity_covers_every_assumption_with_a_range():
    rows = mm.sensitivity()
    assert len(rows) == len(mm.SENSITIVITY_KEYS)
    assert all(r["som_low"] <= r["base"] <= r["som_high"] or r["som_high"] <= r["base"] <= r["som_low"] for r in rows)
    assert rows == sorted(rows, key=lambda r: -r["swing"])


def test_every_assumption_is_labelled():
    for key, item in mm.A.items():
        if key.startswith("_"):
            continue
        assert item.get("type") in {"sourced", "assumption", "sourced-secondary"}, key
        if item["type"] == "assumption" and key != "som_share_of_sam" and key != "fx_idr_per_usd":
            assert "low" in item and "high" in item, key


def test_every_data_url_is_listed_in_sources():
    sources = (ROOT / "data" / "sources.md").read_text()
    import csv

    for name in ["market_size_estimates.csv", "sunscreen_brand_share.csv", "price_observations.csv"]:
        for row in csv.DictReader(open(ROOT / "data" / name)):
            assert row["url"] in sources, row["url"]
