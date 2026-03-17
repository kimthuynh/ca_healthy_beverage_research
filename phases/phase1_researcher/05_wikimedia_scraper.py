"""
05_wikimedia_scraper.py
Pull Wikipedia pageview trends per brand via Wikimedia REST API.
Outputs: data/raw/wikimedia_raw.csv
         data/processed/wikimedia_summary.csv
"""

import csv
import os
import time

import requests

from config.settings import (
    DATA_RAW, DATA_PROCESSED,
    WIKIMEDIA_PROJECT, WIKIMEDIA_ACCESS, WIKIMEDIA_AGENT,
    WIKIMEDIA_GRANULARITY, WIKIMEDIA_START, WIKIMEDIA_END,
)
from config.keywords import ALL_BRANDS, WIKIPEDIA_ARTICLE_TITLES

WIKIMEDIA_BASE = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
HEADERS = {"User-Agent": "BeverageIntelProject/1.0 (research@internal)"}


def fetch_pageviews(article: str) -> list[dict]:
    """Fetch monthly pageviews for one Wikipedia article."""
    url = (
        f"{WIKIMEDIA_BASE}/{WIKIMEDIA_PROJECT}/{WIKIMEDIA_ACCESS}/"
        f"{WIKIMEDIA_AGENT}/{article}/{WIKIMEDIA_GRANULARITY}/"
        f"{WIKIMEDIA_START}/{WIKIMEDIA_END}"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 404:
            return []  # article doesn't exist
        resp.raise_for_status()
        return resp.json().get("items", [])
    except Exception as e:
        print(f"    Wikimedia error for '{article}': {e}")
        return []


def compute_momentum(views_list: list[int]) -> float:
    """Last 3 months avg vs prior 3 months avg."""
    if len(views_list) < 6:
        return 0.0
    recent = sum(views_list[-3:]) / 3
    prior = sum(views_list[-6:-3]) / 3
    if prior == 0:
        return 0.0
    return round((recent - prior) / prior * 100, 2)


def run():
    os.makedirs(DATA_RAW, exist_ok=True)
    os.makedirs(DATA_PROCESSED, exist_ok=True)

    raw_rows = []
    summary_rows = []

    for brand in ALL_BRANDS:
        # Titles from keywords.py use spaces; URL-encode for the API path
        title = WIKIPEDIA_ARTICLE_TITLES.get(brand, brand)
        article = title.replace(" ", "_")
        print(f"  Wikimedia: {brand} → {article}")

        items = fetch_pageviews(article)
        views_by_month = []

        for item in items:
            views = item.get("views", 0)
            timestamp = item.get("timestamp", "")
            views_by_month.append(views)
            raw_rows.append({
                "brand": brand,
                "article": article,
                "timestamp": timestamp,
                "views": views,
            })

        avg_views = round(sum(views_by_month) / len(views_by_month), 1) if views_by_month else 0
        peak_month = ""
        if views_by_month and items:
            peak_idx = views_by_month.index(max(views_by_month))
            peak_month = items[peak_idx].get("timestamp", "")[:6]  # YYYYMM

        momentum = compute_momentum(views_by_month)

        summary_rows.append({
            "brand": brand,
            "article": article,
            "months_collected": len(views_by_month),
            "avg_monthly_views": avg_views,
            "peak_month": peak_month,
            "momentum_pct": momentum,
        })
        print(f"    → {len(views_by_month)} months | avg {avg_views:,.0f} views | momentum {momentum}%")

        time.sleep(0.5)  # be polite to Wikimedia

    # Save raw
    raw_path = os.path.join(DATA_RAW, "wikimedia_raw.csv")
    if raw_rows:
        with open(raw_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["brand", "article", "timestamp", "views"])
            writer.writeheader()
            writer.writerows(raw_rows)
        print(f"\nSaved {len(raw_rows)} rows → {raw_path}")

    # Save summary
    summary_path = os.path.join(DATA_PROCESSED, "wikimedia_summary.csv")
    if summary_rows:
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"Saved {len(summary_rows)} rows → {summary_path}")


if __name__ == "__main__":
    run()
