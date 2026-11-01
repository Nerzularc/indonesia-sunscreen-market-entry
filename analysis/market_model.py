"""TAM / SAM / SOM model for facial sunscreen in Indonesia, with triangulation
and sensitivity analysis.

    python analysis/market_model.py      # prints results, writes analysis/results.json

Two independent estimates of the total market (TAM):
  A. Bottom-up  — population × usage × units per year × average realised price
  B. Top-down   — tracked e-commerce sales (Compas) grown to 2026 ÷ e-commerce
                  share of purchases
If the two land in the same range, the estimate is credible; the gap between
them is reported, not hidden.

SAM = TAM × online share × Java × premium-mass price tier   (what the client can serve)
SOM = SAM × achievable share by year 3                       (what the client can win)
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = json.loads((ROOT / "data" / "assumptions.json").read_text())


def v(a: dict, key: str, which: str = "value") -> float:
    item = a[key]
    return item.get(which, item.get("value"))


def bottom_up(a: dict) -> dict:
    """Retail value in IDR for 2026 (population and usage from 2024-25 surveys)."""
    w, m = v(a, "women_15_34_m") * 1e6, v(a, "men_15_34_m") * 1e6
    ud, uo = v(a, "units_per_daily_user"), v(a, "units_per_occasional_user")
    w_daily, w_occ = v(a, "women_daily_use"), v(a, "women_any_use") - v(a, "women_daily_use")
    m_daily, m_occ = v(a, "men_daily_use"), v(a, "men_any_use") - v(a, "men_daily_use")
    units_w = w * (w_daily * ud + w_occ * uo)
    units_m = m * (m_daily * ud + m_occ * uo)
    core = (units_w + units_m) * v(a, "avg_realised_price_idr")
    total = core * (1 + v(a, "age_35_plus_uplift"))
    return {"units_women_m": units_w / 1e6, "units_men_m": units_m / 1e6,
            "core_15_34_idr_bn": core / 1e9, "tam_idr_bn": total / 1e9}


def top_down(a: dict) -> dict:
    h1_2024 = v(a, "ecom_sunscreen_h1_2024_idr_bn")
    ecom_2024 = h1_2024 * 2  # assume H2 ≈ H1 (H2 has 11.11/12.12 peaks; H1 has Ramadan)
    g = v(a, "ecom_growth_2025_2026")
    ecom_2026 = ecom_2024 * (1 + g) ** 2
    return {"ecom_2024_idr_bn": ecom_2024, "ecom_2026_idr_bn": ecom_2026,
            "tam_idr_bn": ecom_2026 / v(a, "ecom_share_of_purchases")}


def funnel(a: dict, tam_idr_bn: float) -> dict:
    sam = tam_idr_bn * v(a, "ecom_share_of_purchases") * v(a, "java_share") * v(a, "premium_mass_tier_share")
    som = {k: sam * a["som_share_of_sam"][k] for k in ("low", "base", "high")}
    return {"sam_idr_bn": sam, "som_idr_bn": som}


def run(a: dict = A) -> dict:
    fx = v(a, "fx_idr_per_usd")
    bu, td = bottom_up(a), top_down(a)
    tam = (bu["tam_idr_bn"] + td["tam_idr_bn"]) / 2
    f = funnel(a, tam)
    to_usd_m = lambda idr_bn: idr_bn * 1e9 / fx / 1e6  # noqa: E731
    return {
        "bottom_up": bu,
        "top_down": td,
        "gap_pct": abs(bu["tam_idr_bn"] - td["tam_idr_bn"]) / tam,
        "tam_idr_bn": tam,
        "tam_usd_m": to_usd_m(tam),
        "sam_idr_bn": f["sam_idr_bn"],
        "sam_usd_m": to_usd_m(f["sam_idr_bn"]),
        "som_idr_bn": f["som_idr_bn"],
        "som_usd_m": {k: to_usd_m(x) for k, x in f["som_idr_bn"].items()},
        "fx": fx,
    }


SENSITIVITY_KEYS = [
    ("avg_realised_price_idr", "Avg. realised price per unit"),
    ("units_per_daily_user", "Units per daily user / year"),
    ("units_per_occasional_user", "Units per occasional user / year"),
    ("age_35_plus_uplift", "Spend from users aged 35+"),
    ("men_daily_use", "Share of men using daily"),
    ("ecom_growth_2025_2026", "E-commerce growth 2025-26"),
    ("premium_mass_tier_share", "Premium-mass tier share"),
]


def sensitivity(a: dict = A) -> list[dict]:
    """One-at-a-time swing of base-case SOM (USD m) to each assumption's low/high."""
    base = run(a)["som_usd_m"]["base"]
    out = []
    for key, label in SENSITIVITY_KEYS:
        res = {}
        for which in ("low", "high"):
            b = copy.deepcopy(a)
            b[key]["value"] = a[key][which]
            res[which] = run(b)["som_usd_m"]["base"]
        out.append({"key": key, "label": label, "low_value": a[key]["low"], "high_value": a[key]["high"],
                    "som_low": res["low"], "som_high": res["high"], "swing": abs(res["high"] - res["low"])})
    out.sort(key=lambda r: -r["swing"])
    return [{"base": base, **r} for r in out]


if __name__ == "__main__":
    r = run()
    s = sensitivity()
    (ROOT / "analysis" / "results.json").write_text(json.dumps({"results": r, "sensitivity": s}, indent=2))
    print(f"Bottom-up TAM : Rp{r['bottom_up']['tam_idr_bn']:,.0f} bn")
    print(f"Top-down  TAM : Rp{r['top_down']['tam_idr_bn']:,.0f} bn   (gap {r['gap_pct']:.0%})")
    print(f"TAM (blended) : Rp{r['tam_idr_bn']:,.0f} bn  ≈ US${r['tam_usd_m']:,.0f} m")
    print(f"SAM           : Rp{r['sam_idr_bn']:,.0f} bn  ≈ US${r['sam_usd_m']:,.1f} m")
    print("SOM (year 3)  : " + " / ".join(f"{k} US${x:,.1f} m" for k, x in r["som_usd_m"].items()))
    print("Sensitivity (base SOM US$%.2f m):" % s[0]["base"])
    for row in s:
        print(f"  {row['label']:<36} {row['som_low']:6.2f} – {row['som_high']:6.2f}")
