"""
02_trends_scraper.py
Pull CA-filtered Google Trends data for all 20 brands via Pytrends.
Outputs: data/raw/google_trends_raw.csv
         data/processed/google_trends_summary.csv
"""

import csv
import os
import time
from itertools import islice

import pandas as pd
from pytrends.request import TrendReq

from config.settings import (
    DATA_RAW, DATA_PROCESSED,
    TRENDS_GEO, TRENDS_TIMEFRAME,
    TRENDS_SLEEP_SECONDS, TRENDS_BATCH_SIZE,
)
from config.keywords import ALL_BRANDS, TRENDS_CATEGORY_TERMS, TRENDS_MOMENTUM_MODIFIERS


def chunked(iterable, size):
    """Yield successive chunks of given size."""
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def fetch_trends_batch(pytrends: TrendReq, keywords: list[str]) -> pd.DataFrame:
    """Fetch weekly interest over time for up to 5 keywords."""
    pytrends.build_payload(
        keywords,
        geo=TRENDS_GEO,
        timeframe=TRENDS_TIMEFRAME,
    )
    df = pytrends.interest_over_time()
    if df.empty:
        return pd.DataFrame()
    return df.drop(columns=["isPartial"], errors="ignore")


def compute_momentum(series: pd.Series) -> float:
    """Compare last 3 months avg vs prior 3 months avg → slope proxy."""
    if len(series) < 6:
        return 0.0
    recent = series.iloc[-13:].mean()   # ~3 months (weekly data)
    prior = series.iloc[-26:-13].mean()
    if prior == 0:
        return 0.0
    return round((recent - prior) / prior * 100, 2)


def run():
    os.makedirs(DATA_RAW, exist_ok=True)
    os.makedirs(DATA_PROCESSED, exist_ok=True)

    pytrends = TrendReq(hl="en-US", tz=420)  # Pacific time

    # Use brand name directly — short and clean, matches how users type in Google.
    # Reddit search variants are too long/specific for Pytrends.
    brand_kw = {brand: brand for brand in ALL_BRANDS}
    brands = list(brand_kw.keys())

    raw_frames = []
    summary_rows = []

    for batch_brands in chunked(brands, TRENDS_BATCH_SIZE):
        batch_kws = [brand_kw[b] for b in batch_brands]
        print(f"  Trends batch: {batch_kws}")

        try:
            df = fetch_trends_batch(pytrends, batch_kws)
        except Exception as e:
            print(f"    Error: {e} — skipping batch")
            time.sleep(TRENDS_SLEEP_SECONDS * 2)
            continue

        if df.empty:
            print("    No data returned")
            time.sleep(TRENDS_SLEEP_SECONDS)
            continue

        # Reshape to long format for raw CSV
        df_reset = df.reset_index().rename(columns={"date": "week"})
        for kw, brand in zip(batch_kws, batch_brands):
            if kw not in df_reset.columns:
                continue
            col_df = df_reset[["week", kw]].copy()
            col_df.columns = ["week", "interest"]
            col_df.insert(0, "brand", brand)
            col_df.insert(1, "keyword", kw)
            raw_frames.append(col_df)

            series = df[kw].dropna()
            avg_interest = round(series.mean(), 2)
            peak_date = series.idxmax().strftime("%Y-%m-%d") if not series.empty else ""
            momentum = compute_momentum(series)

            summary_rows.append({
                "brand": brand,
                "keyword": kw,
                "avg_interest": avg_interest,
                "peak_date": peak_date,
                "momentum_pct": momentum,
            })

        time.sleep(TRENDS_SLEEP_SECONDS)

    # Save raw
    raw_path = os.path.join(DATA_RAW, "google_trends_raw.csv")
    if raw_frames:
        raw_df = pd.concat(raw_frames, ignore_index=True)
        raw_df.to_csv(raw_path, index=False)
        print(f"\nSaved {len(raw_df)} rows → {raw_path}")
    else:
        print("No raw trends data collected.")

    # Save summary
    summary_path = os.path.join(DATA_PROCESSED, "google_trends_summary.csv")
    if summary_rows:
        pd.DataFrame(summary_rows).to_csv(summary_path, index=False)
        print(f"Saved {len(summary_rows)} rows → {summary_path}")


if __name__ == "__main__":
    run()
