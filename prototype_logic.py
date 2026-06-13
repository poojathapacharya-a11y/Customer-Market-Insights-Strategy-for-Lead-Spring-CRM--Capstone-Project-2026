"""
Lead Spring CRM - Marketing Decision Support System prototype logic.

This script uses the CSV sheets exported from the project workbook and creates
dashboard_data.js for the browser prototype. It uses only Python's standard
library so it can run without pandas or other packages:

    python prototype_logic.py

Then open mdss_dashboard.html in a browser.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
LEADS_CSV = BASE_DIR / "lead_profiles_wba.csv"
BENCHMARKS_CSV = BASE_DIR / "marketing_channel_real_benchmarks.csv"
PRICING_CSV = BASE_DIR / "real_ad_pricing_models_meta_google_tiktok.csv"
RECOMMENDATIONS_CSV = BASE_DIR / "realistic_channel_recommendations.csv"
OUTPUT_JS = BASE_DIR / "dashboard_data.js"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_budget_range(value: str) -> tuple[int, int]:
    numbers = [int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", value or "")]
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return 0, 0


def package_score(package: str) -> int:
    return {"Starter": 20, "Growth": 35, "Premium": 50}.get(package, 20)


def level_score(level: str) -> int:
    return {"Low": 5, "Medium": 15, "High": 25}.get(level, 10)


def score_lead(lead: dict[str, str], recommendation: dict[str, str]) -> int:
    """Transparent rule-based scoring for the academic prototype."""
    base = int(float(lead.get("Priority Score") or 0))
    crm = level_score(lead.get("CRM Need Level", ""))
    digital = level_score(lead.get("Digital Readiness", ""))
    package = package_score(lead.get("Recommended Package", ""))
    has_website = 10 if lead.get("Website") else 0
    has_tiktok = 5 if "Yes" in recommendation.get("TikTok Fit", "") else 0
    score = round((base * 0.45) + crm + (digital * 0.6) + (package * 0.35) + has_website + has_tiktok)
    return max(0, min(100, score))


def make_follow_up(lead: dict[str, str], recommendation: dict[str, str]) -> str:
    name = lead["Business Name"]
    segment = lead["Industry Segment"].lower()
    package = lead["Recommended Package"]
    channels = recommendation["Recommended Platform Mix"]
    return (
        f"Hi {name}, I noticed your business sits in the {segment} segment. "
        f"Based on your likely CRM need and digital readiness, a {package} package "
        f"with {channels} would be a practical starting point. Lead Spring CRM can "
        "help connect your customer data, follow-up process, and campaign reporting "
        "so marketing spend is easier to measure."
    )


def counts(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(Counter(row.get(field, "Unknown") or "Unknown" for row in rows))


def main() -> None:
    leads = read_csv(LEADS_CSV)
    benchmarks = read_csv(BENCHMARKS_CSV)
    pricing = read_csv(PRICING_CSV)
    recommendations = read_csv(RECOMMENDATIONS_CSV)

    rec_by_name = {row["Business Name"]: row for row in recommendations}
    enriched = []
    for lead in leads:
        rec = rec_by_name.get(lead["Business Name"], {})
        low, high = parse_budget_range(rec.get("Realistic Monthly Ad Budget", ""))
        row = {
            **lead,
            "Final Lead Score": score_lead(lead, rec),
            "Priority Band": "Hot" if score_lead(lead, rec) >= 85 else "Warm" if score_lead(lead, rec) >= 70 else "Nurture",
            "Recommended Platform Mix": rec.get("Recommended Platform Mix", ""),
            "TikTok Fit": rec.get("TikTok Fit", ""),
            "Realistic Monthly Ad Budget": rec.get("Realistic Monthly Ad Budget", ""),
            "Budget Low": low,
            "Budget High": high,
            "Relevant Real Price Benchmark": rec.get("Relevant Real Price Benchmark", ""),
            "Reason": rec.get("Reason", ""),
            "Lead Source URL": rec.get("Lead Source URL", lead.get("Source", "")),
            "Pricing Source URLs": rec.get("Pricing Source URLs", ""),
            "Follow-up Message": make_follow_up(lead, rec),
        }
        enriched.append(row)

    payload = {
        "leads": enriched,
        "benchmarks": benchmarks,
        "pricingModels": pricing,
        "summary": {
            "totalLeads": len(enriched),
            "hotLeads": sum(1 for row in enriched if row["Priority Band"] == "Hot"),
            "avgScore": round(sum(row["Final Lead Score"] for row in enriched) / max(len(enriched), 1), 1),
            "packageCounts": counts(enriched, "Recommended Package"),
            "crmNeedCounts": counts(enriched, "CRM Need Level"),
            "digitalReadinessCounts": counts(enriched, "Digital Readiness"),
            "segmentCounts": counts(enriched, "Industry Segment"),
        },
    }

    OUTPUT_JS.write_text(
        "window.dashboardData = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_JS}")


if __name__ == "__main__":
    main()
