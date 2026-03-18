"""
Phase 2 runner — loads and validates all Phase 1 CSVs.
Call load_all_data() before launching the Streamlit app.
"""

from pathlib import Path

import pandas as pd

DATA_RAW = Path("data/raw")
DATA_PROCESSED = Path("data/processed")
DATA_OUTPUT = Path("data/output")

REQUIRED_FILES = {
    "top10": DATA_OUTPUT / "top10_validated.csv",
    "sentiment": DATA_PROCESSED / "brand_sentiment_summary.csv",
    "trends_raw": DATA_RAW / "google_trends_raw.csv",
    "purchase": DATA_PROCESSED / "purchase_channel_summary.csv",
    "youtube": DATA_PROCESSED / "youtube_summary.csv",
    "wikimedia": DATA_PROCESSED / "wikimedia_summary.csv",
}

REQUIRED_COLUMNS = {
    "top10":     ["brand", "composite_score", "trends_avg", "trends_momentum_shifted"],
    "sentiment": ["brand", "vader_pos", "vader_neu", "vader_neg"],
    "trends_raw":["brand", "week", "interest"],
    "purchase":  ["brand", "online_pct", "instore_pct"],
    "youtube":   ["brand", "total_views", "total_comments", "engagement_score"],
    "wikimedia": ["brand", "avg_monthly_views", "momentum_pct"],
}


def _validate(key: str, df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS[key] if c not in df.columns]
    if missing:
        raise ValueError(f"{key}: missing columns {missing}")


def load_all_data() -> dict[str, pd.DataFrame]:
    """Load and validate all CSVs. Raises on missing files or columns."""
    data = {}
    for key, path in REQUIRED_FILES.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing: {path}")
        df = pd.read_csv(path)
        _validate(key, df)
        data[key] = df
    return data


def summarize_top10(df: pd.DataFrame) -> dict:
    """Quick summary stats for header metrics."""
    top = df.sort_values("composite_score", ascending=False).iloc[0]
    return {
        "total_brands": len(df),
        "top_brand": top["brand"],
        "avg_score": round(df["composite_score"].mean(), 1),
        "avg_momentum": round(df["trends_momentum_shifted"].mean(), 1),
    }
