"""
03_serp_scraper.py
Query purchase channel signals (online vs in-store) via SerpAPI.
Outputs: data/raw/purchase_signals_raw.csv
         data/processed/purchase_channel_summary.csv
"""

import csv
import os

import requests

from config.settings import (
    SERPAPI_KEY, DATA_RAW, DATA_PROCESSED,
    SERP_MAX_QUERIES_PER_BRAND, SERP_LOCATION, SERP_NUM_RESULTS,
)
from config.keywords import ALL_BRANDS, SERP_QUERY_TEMPLATES, SERP_PURCHASE_TERMS, SERP_INSTORE_TERMS


def classify_channel(title: str, snippet: str) -> str:
    """Classify result as online, instore, or unknown."""
    text = (title + " " + snippet).lower()
    online = any(s in text for s in SERP_PURCHASE_TERMS)
    instore = any(s in text for s in SERP_INSTORE_TERMS)
    if online and not instore:
        return "online"
    if instore and not online:
        return "instore"
    if online and instore:
        return "both"
    return "unknown"


def serp_search(query: str) -> list[dict]:
    """Call SerpAPI shopping/organic search, return results list."""
    params = {
        "q": query,
        "location": SERP_LOCATION,
        "hl": "en",
        "gl": "us",
        "num": SERP_NUM_RESULTS,
        "api_key": SERPAPI_KEY,
    }
    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        # Combine organic + shopping results
        results = data.get("organic_results", []) + data.get("shopping_results", [])
        return results
    except Exception as e:
        print(f"    SerpAPI error for '{query}': {e}")
        return []


def run():
    os.makedirs(DATA_RAW, exist_ok=True)
    os.makedirs(DATA_PROCESSED, exist_ok=True)

    raw_path = os.path.join(DATA_RAW, "purchase_signals_raw.csv")
    summary_path = os.path.join(DATA_PROCESSED, "purchase_channel_summary.csv")

    raw_rows = []
    summary_rows = []

    for brand in ALL_BRANDS:
        print(f"  SERP: {brand}")
        queries = [t.format(brand=brand) for t in SERP_QUERY_TEMPLATES]
        queries = queries[:SERP_MAX_QUERIES_PER_BRAND]

        brand_channels = []

        for query in queries:
            results = serp_search(query)
            for r in results:
                title = r.get("title", "")
                snippet = r.get("snippet", r.get("price", ""))
                link = r.get("link", r.get("source", ""))
                channel = classify_channel(title, snippet)
                brand_channels.append(channel)
                raw_rows.append({
                    "brand": brand,
                    "query": query,
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                    "channel": channel,
                })

        total = len(brand_channels)
        online_pct = round(brand_channels.count("online") / total * 100, 1) if total else 0
        instore_pct = round(brand_channels.count("instore") / total * 100, 1) if total else 0
        both_pct = round(brand_channels.count("both") / total * 100, 1) if total else 0

        summary_rows.append({
            "brand": brand,
            "total_results": total,
            "online_pct": online_pct,
            "instore_pct": instore_pct,
            "both_pct": both_pct,
            "serp_presence_score": min(total / SERP_NUM_RESULTS, 1.0),  # normalized 0-1
        })
        print(f"    → {total} results | online {online_pct}% | instore {instore_pct}%")

    # Save raw
    if raw_rows:
        with open(raw_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=raw_rows[0].keys())
            writer.writeheader()
            writer.writerows(raw_rows)
        print(f"\nSaved {len(raw_rows)} rows → {raw_path}")

    # Save summary
    if summary_rows:
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"Saved {len(summary_rows)} rows → {summary_path}")


if __name__ == "__main__":
    run()
