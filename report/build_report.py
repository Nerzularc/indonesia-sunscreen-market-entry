"""Build the PDF market-entry brief from the model results and figures.

    python analysis/market_model.py && python analysis/charts.py && python report/build_report.py
"""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "report" / "figures"
OUT = ROOT / "report" / "Indonesia_Sunscreen_Market_Entry_Brief.pdf"
RES = json.loads((ROOT / "analysis" / "results.json").read_text())
R, S = RES["results"], RES["sensitivity"]

BLUE = colors.HexColor("#2a78d6")
INK = colors.HexColor("#0b0b0b")
INK2 = colors.HexColor("#52514e")
GRID = colors.HexColor("#e1e0d9")
SOFT = colors.HexColor("#f2f6fc")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=INK, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=INK, spaceBefore=10, spaceAfter=4)
BODY = ParagraphStyle("B", parent=ss["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13.6, textColor=INK, alignment=TA_LEFT, spaceAfter=5)
SMALL = ParagraphStyle("S", parent=BODY, fontSize=7.8, leading=10.5, textColor=INK2)
BUL = ParagraphStyle("BUL", parent=BODY, leftIndent=10, bulletIndent=0, spaceAfter=2.5)
CALL = ParagraphStyle("CALL", parent=BODY, fontSize=10, leading=14.5)

usd = lambda v: f"US${v:,.1f}M" if v < 100 else f"US${v:,.0f}M"  # noqa: E731
idr = lambda bn: f"Rp{bn / 1000:,.2f} trillion" if bn >= 1000 else f"Rp{bn:,.0f} billion"  # noqa: E731


def P(t, st=BODY):
    return Paragraph(t, st)


def bullets(items):
    return [Paragraph(i, BUL, bulletText="•") for i in items]


def fig(name, width_mm=165, caption=None):
    img = Image(str(FIG / name))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width_mm * mm
    img.drawHeight = width_mm * mm * ratio
    parts = [img]
    if caption:
        parts.append(P(caption, SMALL))
    return KeepTogether(parts + [Spacer(1, 6)])


def table(rows, widths, header=True, zebra=True):
    data = [[P(str(c), SMALL if i else ParagraphStyle("th", parent=SMALL, fontName="Helvetica-Bold", textColor=INK)) for c in r]
            for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK2),
             ("LINEBELOW", (0, 1), (-1, -1), 0.3, GRID), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    t.setStyle(TableStyle(style))
    return t


def callout(flowables):
    t = Table([[flowables]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT), ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(INK2)
    canvas.drawString(20 * mm, 10 * mm, "Indonesia Facial Sunscreen — Market Entry Brief · November 2026 · Prepared by Nuzul Nur Robbulizzat")
    canvas.drawRightString(190 * mm, 10 * mm, f"{doc.page}")
    canvas.restoreState()


def build():
    som = R["som_usd_m"]
    som_idr = R["som_idr_bn"]
    top = S[0]
    story = []

    # ---------------- Cover ----------------
    story += [Spacer(1, 40 * mm),
              P("MARKET ENTRY BRIEF", ParagraphStyle("k", parent=SMALL, fontName="Helvetica-Bold", textColor=BLUE, fontSize=9)),
              P("Should a Korean sunscreen brand enter Indonesia in 2027?", ParagraphStyle("t", parent=H1, fontSize=24, leading=29)),
              Spacer(1, 4),
              P("Market sizing, competition, consumers, channels and regulation for facial sunscreen in Indonesia — "
                "with a recommended go-to-market plan.", ParagraphStyle("st", parent=BODY, fontSize=11.5, leading=16, textColor=INK2)),
              Spacer(1, 14 * mm),
              table([["Prepared for", "Haneul Skin (fictional client used for this portfolio case)"],
                     ["Prepared by", "Nuzul Nur Robbulizzat — Information Systems, Institut Teknologi Sepuluh Nopember (ITS), Surabaya"],
                     ["Date", "1 November 2026"],
                     ["Method", "Desk research (BPS, Compas, Jakpat, Snapcart, Momentum Works, BPJPH, industry reports), "
                                "two-way market triangulation, sensitivity analysis. All model inputs are in data/assumptions.json."]],
                    [32, 138], header=False),
              Spacer(1, 12 * mm),
              P("Note: the client brand is fictional. Market data are from the public sources listed on the last page; "
                "figures marked as assumptions are analyst estimates and are stress-tested in Section 8.", SMALL),
              PageBreak()]

    # ---------------- 1. Executive summary ----------------
    story += [P("1. Executive summary", H1),
              callout([P(f"<b>Recommendation: GO — but as a focused online challenger, not a mass-market launch.</b> "
                         f"Facial sunscreen in Indonesia is a ~{usd(R['tam_usd_m'])} market ({idr(R['tam_idr_bn'])}) that is growing "
                         f"fast, fragmented, and sold mostly online. The realistic prize for a new premium-mass brand is "
                         f"<b>{usd(som['base'])} a year by year 3</b> (range {usd(som['low'])}–{usd(som['high'])}), "
                         f"which justifies entry only with a lean, online-first model and a local partner for registration.", CALL)]),
              Spacer(1, 8)]
    story += bullets([
        f"<b>The market is large and still growing.</b> Two independent methods put 2026 retail value at "
        f"{usd(R['top_down']['tam_idr_bn'] * 1e9 / R['fx'] / 1e6)}–{usd(R['bottom_up']['tam_idr_bn'] * 1e9 / R['fx'] / 1e6)}. "
        "Tracked e-commerce sunscreen sales jumped 72% from H2 2023 (Rp530 bn) to H1 2024 (Rp914 bn).",
        "<b>Demand is real but shallow.</b> 75% of women and 42% of men use sunscreen, yet only about a third of women apply it daily — "
        "the growth lever is converting occasional users into daily users with formats that feel good in heat and humidity.",
        "<b>No one owns the category.</b> The top four brands hold only ~26.5% of e-commerce sunscreen sales. Local brands lead "
        "(Wardah, Azarine, Facetology); Skintific shows a foreign-founded brand can reach the top four through TikTok-first marketing.",
        "<b>Price is the battlefield.</b> Leaders sell at Rp10k–21k per 10 ml. A Korean brand cannot win on price; it should sit "
        "at Rp89k–129k per 40 ml with a visible reason to pay more (texture, tone-up, sensitive-skin claims, K-beauty credibility).",
        "<b>Two platforms are the market.</b> Shopee (54%) and TikTok Shop + Tokopedia (38%) hold ~92% of e-commerce GMV.",
        "<b>Regulation is the critical path.</b> A BPOM notification through a local registrant is mandatory before sale. Halal "
        "certification for cosmetics became mandatory on 17 Oct 2026; on 16 Oct 2026 the government announced a proposed extension "
        "to 17 Oct 2028 that still needs formal publication. Plan to certify anyway — it is also a purchase driver.",
    ])
    story += [P("Decision summary", H2),
              table([["Question", "Answer"],
                     ["Is the market big enough?", f"Yes — TAM ~{usd(R['tam_usd_m'])}; serviceable market (online, Java, premium-mass) ~{usd(R['sam_usd_m'])}."],
                     ["Can a new brand win share?", "Yes, if focused: fragmented leaders, creator-driven discovery, low switching costs."],
                     ["How?", "Hero SKU, Shopee Mall + TikTok Shop, affiliate creators, ingredient-led listings, Java first."],
                     ["What could kill it?", "Price war from local brands, slow BPOM/halal approval, under-funded creator marketing."],
                     ["What to decide next?", "Pick the local registrant/distributor and budget months 0–6 (Section 7)."]],
                    [48, 122]),
              PageBreak()]

    # ---------------- 2. Market size ----------------
    story += [P("2. How big is the market?", H1),
              P("Published estimates for the overall <b>skin care</b> market cluster around US$3 billion for 2025, with one outlier. "
                "No public source sizes facial sunscreen on its own, so we estimate it two ways and compare."),
              fig("01_skincare_estimates.png", 135, "Figure 1 — Third-party estimates of Indonesia's skin care market, 2025. Sources: see page 'Sources'."),
              P("<b>Bottom-up:</b> women and men aged 15–34 (BPS 2025 projections: 43.3 M and 45.6 M) × share using sunscreen "
                "(Jakpat: 75% / 42%), split into daily users (Snapcart: 35% of women; 10% of men assumed) and occasional users × "
                "units per year (4 daily, 1.5 occasional — assumptions) × average realised price (Rp40,000 per unit — assumption), "
                "plus 25% for users aged 35+. Result: "
                f"<b>{idr(R['bottom_up']['tam_idr_bn'])}</b>."),
              P("<b>Top-down:</b> Compas tracked Rp914 bn of e-commerce sunscreen sales in H1 2024. Doubling for the full year and growing "
                "25% a year (assumption) gives "
                f"{idr(R['top_down']['ecom_2026_idr_bn'])} online in 2026; dividing by e-commerce's ~68% share of skincare purchases "
                f"gives <b>{idr(R['top_down']['tam_idr_bn'])}</b>."),
              fig("02_tam_triangulation.png", 118, f"Figure 2 — The two methods differ by {R['gap_pct']:.0%}; we use the average and report the range. "
                  f"Cross-check: {usd(R['tam_usd_m'])} is ~{R['tam_usd_m'] / 3070:.0%} of the US$3.07B skin care market — plausible for one core category."),
              P("<b>Serviceable and obtainable market.</b> The client can realistically serve shoppers who buy online (68%), live on Java "
                "(55.65% of the population, BPS SUPAS 2025) and buy in the Rp80k–130k tier (25% of value — assumption). A year-3 share of 4% of "
                "that segment is the base case; for reference, the #4 brand nationally (Skintific) holds ~5.2% of all e-commerce sunscreen sales."),
              fig("03_tam_sam_som.png", 150, f"Figure 3 — TAM {usd(R['tam_usd_m'])} → SAM {usd(R['sam_usd_m'])} → SOM {usd(som['base'])} "
                  f"(≈ {idr(som_idr['base'])}, roughly 180k units a year at Rp109k)."),
              Spacer(1, 8)]

    # ---------------- 3. Consumers ----------------
    story += [P("3. Who buys, and why", H1),
              fig("06_usage.png", 150, "Figure 4 — Sunscreen use by gender. Sources: Jakpat Beauty Trends 2024; Snapcart survey of Indonesian women."),
              P("Sunscreen is now a core routine product: in Jakpat's September 2025 survey it ranks in the top three skincare products "
                "after cleanser (91%), and its importance grew from 2024 to 2025. Women run longer morning routines led by cleanser and sunscreen; "
                "men keep simpler routines — a later opportunity for a no-white-cast, matte formula."),
              P("Key insights for positioning:"),
              ] + bullets([
                  "<b>Local fit beats foreign prestige.</b> 87% of Gen Z and Millennial respondents use domestic skincare (Populix 2025), and "
                  "73% of women in a Jakpat survey said local products suit their skin better. A Korean brand must prove it is <i>made for "
                  "tropical, humid skin</i>, not just imported.",
                  "<b>Ingredients sell.</b> Products with ingredient keywords such as niacinamide, retinol and vitamin C in their titles had 56% "
                  "higher sales across 38,000 brands studied by Compas — listing copy is a growth lever, not admin.",
                  "<b>Weather moves demand.</b> Compas observed a sharp sunscreen spike in October 2023 during a heatwave; campaigns should be "
                  "ready to react to UV and heat news.",
                  "<b>Daily habit is the gap.</b> Only ~35% of women apply sunscreen daily. Textures that sit well under makeup and in humidity "
                  "(tone-up, serum, mist for reapplication) convert occasional users.",
              ]) + [PageBreak()]

    # ---------------- 4. Competition ----------------
    story += [P("4. Competitive landscape", H1),
              fig("04_brand_share.png", 150, "Figure 5 — Top sunscreen brands by share of e-commerce sales, Jan–Sep 2025 (top four combined: 26.5%; Compas analysis of Shopee, "
                  "TikTok Shop, Tokopedia, Lazada and Blibli, via GoodStats). On Shopee in Q2 2026 the leaders were Wardah 10.4%, Facetology 7.5%, Azarine 6.3%."),
              P("The category is <b>led by local brands but not concentrated</b>: the top four hold about a quarter of sales and the rest is a long "
                "tail. Brand positions shift quarter to quarter, which shows how much creator content and promotions move share."),
              fig("05_price_positioning.png", 165, "Figure 6 — Observed prices per 10 ml for best-selling SKUs on Lazada and Tokopedia (2026 listings, incl. "
                  "platform discounts; multi-packs divided per unit; two sizes assumed). Snapshot, not an audit — verify before pricing."),
              P("Leaders compete at <b>Rp10k–21k per 10 ml</b> and use twin packs to push price per unit lower. Tinted and skin-tint "
                "formats (Skintific, Amaterasun) already sell at Rp27k–31k per 10 ml, which is the space a K-beauty entrant can credibly occupy."),
              table([["Competitor", "Edge", "Weak spot for an entrant to exploit"],
                     ["Wardah", "Halal pioneer, offline + online reach, wide SPF range", "Mass positioning; less 'trend' credibility with Gen Z"],
                     ["Azarine", "Price leadership, K-pop ambassador, twin packs", "Low price leaves little room for premium story"],
                     ["Facetology", "Fast growth since 2022, makeup-like finish", "Concentrated in a few hero SKUs"],
                     ["Skintific", "TikTok-first playbook, science claims", "Same playbook is copyable; competes in the same premium-mass band"]],
                    [30, 70, 70]),
              PageBreak()]

    # ---------------- 5. Channels ----------------
    story += [P("5. Where to sell", H1),
              fig("07_platforms.png", 150, "Figure 7 — Share of e-commerce GMV by platform, 2025 (Momentum Works via Bisnis.com, 16 May 2026)."),
              ] + bullets([
                  "<b>Shopee Mall</b> is the default: it led beauty e-commerce sales in every Compas cut we found, and in 2025 it held 74.5% of local-brand "
                  "beauty bundle sales.",
                  "<b>TikTok Shop</b> (merged with Tokopedia) is the discovery engine: Shop|Tokopedia grew 59% in 2025, the fastest of any platform (Compas). "
                  "Launch with affiliate creators and live selling, not only paid ads.",
                  "<b>Offline</b> (Watsons, Guardian, Sociolla stores) adds trust and trial but needs distributor margins and inventory — phase 2.",
                  "<b>Campaign calendar:</b> Ramadan, 11.11, 12.12 and payday dates drive a disproportionate share of beauty sales; Compas specifically "
                  "advises brands to use double-date campaigns.",
              ]) + [Spacer(1, 6)]

    # ---------------- 6. Regulation ----------------
    story += [P("6. Regulatory path", H1),
              table([["Requirement", "What it means for the client", "Status / timing"],
                     ["BPOM cosmetic notification", "Needed before importing, advertising or selling. Foreign manufacturers cannot register directly — "
                      "a local legal entity or appointed registrant files it.", "Mandatory now. Budget several months; start first."],
                     ["Halal certification (BPJPH)", "Applies to imported and local cosmetics. Certification must come from BPJPH or a recognised foreign "
                      "halal body; ingredients and suppliers are reviewed.", "Deadline 17 Oct 2026, enforced from 18 Oct (BPJPH confirmed on 16 Sep 2026). "
                      "On 16 Oct 2026 a proposed extension to 17 Oct 2028 was announced — not yet formally published."],
                     ["Labelling & claims", "Indonesian-language label, BPOM number, halal logo; SPF/PA claims must be supported by tests.", "Before first shipment."],
                     ["Enforcement climate", "BPOM has seized over 2 million unregistered cosmetics, mostly imports — grey-market entry is not an option.",
                      "Ongoing."]],
                    [38, 82, 50]),
              Spacer(1, 4),
              P("Because the halal deadline may move, the recommendation does not depend on it: certify before launch. It removes legal risk and "
                "matters commercially in a market where the category leader (Wardah) built its brand on halal.", SMALL),
              PageBreak()]

    # ---------------- 7. Plan ----------------
    story += [P("7. Recommended go-to-market plan", H1),
              P("<b>Positioning:</b> \"Korean UV science, made for Indonesian heat\" — a lightweight, tone-up SPF50+ PA++++ that stays matte in humidity, "
                "halal certified, tested on Indonesian skin. Hero SKU 40 ml at <b>Rp109k</b> (launch band Rp89k–129k), plus a reapplication mist in phase 2."),
              table([["Phase", "Months", "Actions", "Exit KPI"],
                     ["0. Compliance", "−6 to 0", "Appoint local registrant/distributor; BPOM notification; halal certification; Indonesian SPF/PA and "
                      "humidity wear tests; label localisation.", "BPOM + halal approved"],
                     ["1. Online launch", "1–6", "Shopee Mall + TikTok Shop official stores; 150–300 micro/mid creators on affiliate commission; ingredient-led "
                      "titles; sampling sachets in orders; launch on a double-date campaign.", "Rating ≥ 4.8, repeat rate ≥ 20%, CAC payback < 3 orders"],
                     ["2. Scale", "7–18", "Live selling; second SKU (mist or skin tint); Watsons/Guardian in Jakarta, Surabaya, Bandung; reviewer program.",
                      "Top 15 in Shopee sunscreen; ≥ 1% online share"],
                     ["3. Expand", "19–36", "Outside Java (Medan, Makassar); men's line; bundles with moisturiser.", f"Year-3 revenue {usd(som['base'])}"]],
                    [26, 18, 92, 34]),
              Spacer(1, 6),
              P("<b>KPIs to track monthly:</b> GMV by platform, share of category (Compas or similar), conversion rate, CAC by channel, repeat "
                "purchase within 60 days, rating and review volume, creator-attributed sales, stock cover of the hero SKU."),
              P("8. What the result depends on", H2),
              fig("08_sensitivity.png", 160, "Figure 8 — One-at-a-time sensitivity of year-3 revenue (base case "
                  f"{usd(top['base'])}). Bars show the range when each assumption moves to its low/high value (data/assumptions.json)."),
              P(f"The answer is most sensitive to <b>{top['label'].lower()}</b> ({usd(top['som_low'])}–{usd(top['som_high'])}) and to "
                f"<b>{S[1]['label'].lower()}</b>. Both can be measured cheaply before committing: a two-week marketplace audit of SKUs priced "
                "Rp80k–130k, and a 300-person online survey on units bought per year."),
              PageBreak()]

    # ---------------- 9. Risks ----------------
    story += [P("9. Risks and mitigations", H1),
              table([["Risk", "Likelihood", "Mitigation"],
                     ["Local brands respond with price cuts and twin packs", "High", "Do not compete on price; compete on texture, tone-up and proof. "
                      "Use bundles, not discounts, during campaigns."],
                     ["Registration or halal approval takes longer than planned", "Medium", "Start Phase 0 immediately; choose a registrant with cosmetic "
                      "track record; prepare ingredient halal documentation from suppliers."],
                     ["Creator marketing costs rise / audience fatigue", "Medium", "Affiliate (commission) model first; track CAC weekly; build owned "
                      "channels (WhatsApp community, reviews)."],
                     ["Formula fails in humidity / reviews flag white cast", "Medium", "Local wear tests before launch; small first batch; fast reformulation loop."],
                     ["Exchange-rate swings squeeze imported margins", "Medium", f"Price in IDR with a buffer; review quarterly (model uses Rp{R['fx']:,}/US$)."],
                     ["Counterfeits and parallel imports", "Medium", "Official stores only; anti-counterfeit labels; report infringing listings."]],
                    [52, 22, 96]),
              Spacer(1, 10),
              P("Methodology and limitations", H2)] + bullets([
                  "Desk research only; no primary survey. Brand shares come from Compas e-commerce tracking reported by GoodStats and partners, "
                  "and exclude offline retail.",
                  "Price observations are a small snapshot of 2026 marketplace listings including discounts; two pack sizes were assumed.",
                  "The e-commerce share of purchases (68%) is a Jakpat figure cited in an academic thesis (secondary source).",
                  "The bottom-up and top-down estimates differ by %d%%; the true value is more likely inside that range than at the midpoint." % round(R["gap_pct"] * 100),
                  "All calculations are reproducible: <font face='Courier'>python analysis/market_model.py</font>.",
              ]) + [PageBreak()]

    # ---------------- Sources ----------------
    src = (ROOT / "data" / "sources.md").read_text().splitlines()
    story += [P("Sources", H1)]
    for line in src:
        if line.startswith("- "):
            story.append(Paragraph(line[2:].replace("&", "&amp;"), ParagraphStyle("src", parent=SMALL, spaceAfter=3)))

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
                            title="Indonesia Facial Sunscreen — Market Entry Brief", author="Nuzul Nur Robbulizzat")
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=on_page)
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
