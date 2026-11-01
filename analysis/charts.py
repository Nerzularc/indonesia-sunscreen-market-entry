"""Figures for the report. Style: thin marks, hairline grid, one hue per job
(validated categorical palette; blue = data, orange = the highlighted entity)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "report" / "figures"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SEQ = ["#9ec5f4", "#5598e7", "#256abf"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "text.color": INK, "axes.labelcolor": INK2,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200, "savefig.bbox": "tight",
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
})


def _hgrid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def read_csv(name):
    with open(ROOT / "data" / name, newline="") as f:
        return list(csv.DictReader(f))


def fig_estimates():
    rows = [r for r in read_csv("market_size_estimates.csv") if "context" not in r["scope"]]
    rows.sort(key=lambda r: float(r["value_usd_bn"]))
    fig, ax = plt.subplots(figsize=(6.2, 2.3))
    names = [r["source"] for r in rows]
    vals = [float(r["value_usd_bn"]) for r in rows]
    ax.barh(names, vals, color=BLUE, height=0.55)
    for i, val in enumerate(vals):
        ax.text(val + 0.06, i, f"${val:.2f}B", va="center", color=INK, fontsize=8.5)
    med = sorted(vals)[len(vals) // 2]
    ax.axvline(med, color=INK2, linewidth=0.8)
    ax.text(med + 0.05, len(vals) - 0.45, f"median ${med:.2f}B", color=INK2, fontsize=8)
    ax.set_xlabel("Indonesia skin care market, 2025 (US$ bn)")
    ax.set_xlim(0, max(vals) * 1.18)
    _hgrid(ax)
    ax.tick_params(axis="y", colors=INK2, length=0)
    fig.savefig(FIG / "01_skincare_estimates.png")
    plt.close(fig)


def fig_triangulation(res):
    r = res["results"]
    fx = r["fx"]
    to_usd = lambda bn: bn * 1e9 / fx / 1e6  # noqa: E731
    labels = ["Bottom-up\npopulation × usage\n× units × price", "Top-down\ne-commerce sales\n÷ online share", "Blended TAM\n(average)"]
    vals = [to_usd(r["bottom_up"]["tam_idr_bn"]), to_usd(r["top_down"]["tam_idr_bn"]), r["tam_usd_m"]]
    colors = [SEQ[0], SEQ[0], BLUE]
    fig, ax = plt.subplots(figsize=(6.2, 2.4))
    bars = ax.bar(labels, vals, color=colors, width=0.5)
    for b, val in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, val + 6, f"US${val:,.0f}M", ha="center", fontsize=8.5, color=INK)
    ax.set_ylabel("2026 retail value (US$ m)")
    ax.set_ylim(0, max(vals) * 1.2)
    _hgrid(ax, "y")
    ax.tick_params(axis="x", colors=INK2, length=0)
    fig.savefig(FIG / "02_tam_triangulation.png")
    plt.close(fig)


def fig_funnel(res):
    r = res["results"]
    stages = [("TAM — all facial sunscreen, Indonesia", r["tam_usd_m"]),
              ("SAM — online, Java, Rp80–130k tier", r["sam_usd_m"]),
              ("SOM — year-3 base case (4% of SAM)", r["som_usd_m"]["base"])]
    fig, ax = plt.subplots(figsize=(6.2, 1.9))
    for i, (label, val) in enumerate(stages):
        ax.barh(i, val, color=SEQ[i], height=0.6)
        ax.text(val + 4, i, f"US${val:,.1f}M" if val < 100 else f"US${val:,.0f}M", va="center", fontsize=8.5)
    ax.set_yticks(range(3), [s[0] for s in stages], color=INK2)
    ax.invert_yaxis()
    ax.set_xlim(0, stages[0][1] * 1.2)
    ax.set_xlabel("US$ m per year")
    ax.tick_params(axis="y", length=0)
    _hgrid(ax)
    fig.savefig(FIG / "03_tam_sam_som.png")
    plt.close(fig)


def fig_brand_share():
    rows = [r for r in read_csv("sunscreen_brand_share.csv") if r["period"].startswith("2025")]
    rows.sort(key=lambda r: float(r["share_pct"]))
    names = [r["brand"] for r in rows] + []
    vals = [float(r["share_pct"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6.2, 2.1))
    ax.barh(names, vals, color=BLUE, height=0.55)
    for i, val in enumerate(vals):
        ax.text(val + 0.12, i, f"{val:.1f}%", va="center", fontsize=8.5)
    ax.set_xlabel("Share of e-commerce sunscreen sales, Jan–Sep 2025 (top 4 brands)")
    ax.set_xlim(0, 10)
    ax.tick_params(axis="y", colors=INK2, length=0)
    _hgrid(ax)
    fig.savefig(FIG / "04_brand_share.png")
    plt.close(fig)


def fig_prices():
    rows = read_csv("price_observations.csv")
    pts = []
    for r in rows:
        per_unit = float(r["observed_price_idr"]) / int(r["units_in_pack"])
        per_10ml = per_unit / float(r["ml_or_g_per_unit"]) * 10
        pts.append((f"{r['brand']} · {r['product'][:28]}", per_10ml))
    pts.sort(key=lambda p: p[1])
    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    y = range(len(pts))
    ax.hlines(y, 0, [p[1] for p in pts], color=GRID, linewidth=1)
    ax.scatter([p[1] for p in pts], y, color=BLUE, s=28, zorder=3, edgecolor="white", linewidth=1)
    ax.axvspan(22250, 32250, color=ORANGE, alpha=0.12, linewidth=0)
    ax.text(22600, -0.2, "Proposed entry band\nRp89–129k per 40 ml", color=INK2, fontsize=7.5, va="bottom")
    for i, (_, val) in enumerate(pts):
        ax.text(val + 600, i, f"Rp{val / 1000:.1f}k", va="center", fontsize=7.5, color=INK)
    ax.set_yticks(list(y), [p[0] for p in pts], fontsize=7.5, color=INK2)
    ax.set_xlabel("Observed price per 10 ml (IDR, incl. platform discounts)")
    ax.set_xlim(0, 36000)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"Rp{x / 1000:.0f}k"))
    ax.tick_params(axis="y", length=0)
    _hgrid(ax)
    fig.savefig(FIG / "05_price_positioning.png")
    plt.close(fig)


def fig_usage():
    fig, ax = plt.subplots(figsize=(6.2, 2.0))
    bars = [(3.0, 75, BLUE), (2.45, 35, ORANGE), (1.2, 42, BLUE)]
    for yy, val, col in bars:
        ax.barh(yy, val, height=0.45, color=col)
        ax.text(val + 1, yy, f"{val}%", va="center", fontsize=8.5)
    ax.text(1, 0.65, "daily use: no published figure for men", fontsize=7.5, color=MUTED, va="center")
    ax.set_yticks([2.72, 0.92], ["Women", "Men"], color=INK2)
    ax.set_ylim(0.3, 3.4)
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of respondents")
    ax.tick_params(axis="y", length=0)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLUE, label="Use sunscreen (Jakpat 2024)"), Patch(color=ORANGE, label="Apply daily (Snapcart)")],
              frameon=False, loc="lower right", fontsize=7.5)
    _hgrid(ax)
    fig.savefig(FIG / "06_usage.png")
    plt.close(fig)


def fig_platforms():
    names = ["Shopee", "TikTok Shop + Tokopedia", "Lazada", "Blibli"]
    vals = [54, 38, 6, 3]
    fig, ax = plt.subplots(figsize=(6.2, 1.7))
    ax.barh(names[::-1], vals[::-1], color=BLUE, height=0.55)
    for i, val in enumerate(vals[::-1]):
        ax.text(val + 0.8, i, f"{val}%", va="center", fontsize=8.5)
    ax.set_xlim(0, 65)
    ax.set_xlabel("Share of Indonesian e-commerce GMV, 2025 (Momentum Works via Bisnis.com)")
    ax.tick_params(axis="y", colors=INK2, length=0)
    _hgrid(ax)
    fig.savefig(FIG / "07_platforms.png")
    plt.close(fig)


def fig_tornado(res):
    s = res["sensitivity"]
    base = s[0]["base"]
    fig, ax = plt.subplots(figsize=(6.2, 2.6))
    for i, row in enumerate(reversed(s)):
        lo, hi = row["som_low"], row["som_high"]
        ax.barh(i, lo - base, left=base, color=ORANGE if lo < base else BLUE, height=0.55)
        ax.barh(i, hi - base, left=base, color=BLUE if hi > base else ORANGE, height=0.55)
        ax.text(min(lo, hi) - 0.02, i, f"${min(lo, hi):.2f}M", ha="right", va="center", fontsize=7.5, color=INK2)
        ax.text(max(lo, hi) + 0.02, i, f"${max(lo, hi):.2f}M", ha="left", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(range(len(s)), [r["label"] for r in reversed(s)], fontsize=8, color=INK2)
    ax.axvline(base, color=INK, linewidth=0.8)
    ax.text(base, len(s) - 0.35, f"base US${base:.2f}M", ha="center", fontsize=7.5)
    ax.set_xlabel("Year-3 revenue (SOM, US$ m) when one assumption moves to its low / high value")
    ax.set_xlim(base - 0.75, base + 0.75)
    ax.tick_params(axis="y", length=0)
    _hgrid(ax)
    fig.savefig(FIG / "08_sensitivity.png")
    plt.close(fig)


def build_all():
    FIG.mkdir(parents=True, exist_ok=True)
    res = json.loads((ROOT / "analysis" / "results.json").read_text())
    fig_estimates()
    fig_triangulation(res)
    fig_funnel(res)
    fig_brand_share()
    fig_prices()
    fig_usage()
    fig_platforms()
    fig_tornado(res)
    print(f"figures → {FIG.relative_to(ROOT)}/")


if __name__ == "__main__":
    build_all()
