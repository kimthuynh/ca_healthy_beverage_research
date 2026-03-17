"""
07_brand_scorer.py
Composite scoring model: normalize 7 signals → weighted score → rank 20 brands → Top 10.
Outputs: data/processed/top20_scored.csv
         data/output/top10_brands.csv
"""

import os

import pandas as pd

from config.settings import DATA_RAW, DATA_PROCESSED, DATA_OUTPUT, SCORE_WEIGHTS
from config.keywords import ALL_BRANDS


def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


def normalize_col(series: pd.Series) -> pd.Series:
    """Min-max normalize to 0-100."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series([50.0] * len(series), index=series.index)
    return (series - mn) / (mx - mn) * 100


def build_signal_table(brands: list[str]) -> pd.DataFrame:
    """Load all processed CSVs and extract one value per signal per brand."""
    df = pd.DataFrame({"brand": brands})

    # --- Reddit signals ---
    reddit = load_csv(os.path.join(DATA_RAW, "reddit_raw.csv"))
    if not reddit.empty:
        r_vol = reddit.groupby("brand").size().reset_index(name="reddit_volume")
        df = df.merge(r_vol, on="brand", how="left")
    else:
        df["reddit_volume"] = 0

    sentiment = load_csv(os.path.join(DATA_PROCESSED, "brand_sentiment_summary.csv"))
    if not sentiment.empty:
        sent_cols = sentiment[["brand", "vader_compound"]].copy()
        # Shift compound (-1 to 1) → 0-100
        sent_cols["sentiment_score"] = (sent_cols["vader_compound"] + 1) / 2 * 100
        df = df.merge(sent_cols[["brand", "sentiment_score"]], on="brand", how="left")
    else:
        df["sentiment_score"] = 50

    # --- Google Trends signals ---
    trends = load_csv(os.path.join(DATA_PROCESSED, "google_trends_summary.csv"))
    if not trends.empty:
        t = trends[["brand", "avg_interest", "momentum_pct"]].copy()
        # Momentum can be negative — shift to 0-based for scoring
        t["trends_momentum_shifted"] = t["momentum_pct"] + 100
        df = df.merge(t[["brand", "avg_interest", "trends_momentum_shifted"]], on="brand", how="left")
        df.rename(columns={"avg_interest": "trends_avg"}, inplace=True)
    else:
        df["trends_avg"] = 0
        df["trends_momentum_shifted"] = 100

    # --- SerpAPI signal ---
    serp = load_csv(os.path.join(DATA_PROCESSED, "purchase_channel_summary.csv"))
    if not serp.empty:
        df = df.merge(serp[["brand", "serp_presence_score"]], on="brand", how="left")
        df["serp_presence_score"] = df["serp_presence_score"] * 100  # convert 0-1 → 0-100
    else:
        df["serp_presence_score"] = 0

    # --- YouTube signal ---
    yt = load_csv(os.path.join(DATA_PROCESSED, "youtube_summary.csv"))
    if not yt.empty:
        df = df.merge(yt[["brand", "engagement_score"]], on="brand", how="left")
        df.rename(columns={"engagement_score": "youtube_engagement"}, inplace=True)
    else:
        df["youtube_engagement"] = 0

    # --- Wikimedia signal ---
    wiki = load_csv(os.path.join(DATA_PROCESSED, "wikimedia_summary.csv"))
    if not wiki.empty:
        w = wiki[["brand", "momentum_pct"]].copy()
        w["wikimedia_momentum_shifted"] = w["momentum_pct"] + 100
        df = df.merge(w[["brand", "wikimedia_momentum_shifted"]], on="brand", how="left")
    else:
        df["wikimedia_momentum_shifted"] = 100

    df.fillna(0, inplace=True)
    return df


def compute_composite_score(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize each signal then apply weighted sum."""
    signal_col_map = {
        "reddit_volume":      "reddit_volume",
        "sentiment_score":    "sentiment_score",
        "trends_avg":         "trends_avg",
        "trends_momentum":    "trends_momentum_shifted",
        "serp_presence":      "serp_presence_score",
        "youtube_engagement": "youtube_engagement",
        "wikimedia_momentum": "wikimedia_momentum_shifted",
    }

    for signal_key, col in signal_col_map.items():
        norm_col = f"norm_{signal_key}"
        df[norm_col] = normalize_col(df[col])

    weights = SCORE_WEIGHTS
    df["composite_score"] = (
        df["norm_reddit_volume"]      * weights["reddit_volume"]      +
        df["norm_sentiment_score"]    * weights["sentiment_score"]    +
        df["norm_trends_avg"]         * weights["trends_avg"]         +
        df["norm_trends_momentum"]    * weights["trends_momentum"]    +
        df["norm_serp_presence"]      * weights["serp_presence"]      +
        df["norm_youtube_engagement"] * weights["youtube_engagement"] +
        df["norm_wikimedia_momentum"] * weights["wikimedia_momentum"]
    ).round(2)

    df.sort_values("composite_score", ascending=False, inplace=True)
    df["rank"] = range(1, len(df) + 1)
    return df


def run():
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    os.makedirs(DATA_OUTPUT, exist_ok=True)

    brands = list(ALL_BRANDS.keys())
    df = build_signal_table(brands)
    df = compute_composite_score(df)

    # Save all 20
    top20_path = os.path.join(DATA_PROCESSED, "top20_scored.csv")
    df.to_csv(top20_path, index=False)
    print(f"Saved top20 → {top20_path}")

    # Save Top 10
    top10 = df.head(10).copy()
    top10_path = os.path.join(DATA_OUTPUT, "top10_brands.csv")
    top10.to_csv(top10_path, index=False)
    print(f"Saved top10 → {top10_path}")

    print("\n--- TOP 10 BRANDS ---")
    for _, row in top10.iterrows():
        print(f"  #{int(row['rank']):2d}  {row['brand']:<25}  score: {row['composite_score']:.1f}")


if __name__ == "__main__":
    run()
