"""
06_sentiment_analyzer.py
VADER per-row sentiment scoring + Claude theme extraction across Reddit + YouTube.
Outputs: data/processed/brand_sentiment_summary.csv
"""

import csv
import json
import os

import anthropic
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config.settings import (
    ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_BATCH_SIZE,
    DATA_RAW, DATA_PROCESSED, PROMPTS_DIR,
)
from config.keywords import ALL_BRANDS


def load_prompt_template() -> str:
    path = os.path.join(PROMPTS_DIR, "sentiment_analyzer.md")
    with open(path, "r") as f:
        return f.read()


def get_brand_category(brand: str) -> str:
    from config.keywords import KOMBUCHA_BRANDS
    return "Kombucha & Fermented Beverages" if brand in KOMBUCHA_BRANDS else "Plant-Based Milk"


def load_text_for_brand(brand: str, reddit_df: pd.DataFrame, youtube_df: pd.DataFrame) -> list[str]:
    """Pull text items for a brand from both sources."""
    texts = []

    if not reddit_df.empty:
        r = reddit_df[reddit_df["brand"] == brand]["text"].dropna()
        texts.extend(r[r.str.len() > 20].tolist())

    if not youtube_df.empty:
        y = youtube_df[youtube_df["brand"] == brand]["text"].dropna()
        texts.extend(y[y.str.len() > 20].tolist())

    return texts


def vader_score_texts(texts: list[str], analyzer: SentimentIntensityAnalyzer) -> dict:
    """Return avg VADER compound score + pos/neg/neu breakdown."""
    if not texts:
        return {"compound": 0.0, "pos": 0.0, "neu": 0.0, "neg": 0.0}

    compounds, pos_list, neu_list, neg_list = [], [], [], []
    for text in texts:
        scores = analyzer.polarity_scores(text)
        compounds.append(scores["compound"])
        pos_list.append(scores["pos"])
        neu_list.append(scores["neu"])
        neg_list.append(scores["neg"])

    n = len(compounds)
    return {
        "compound": round(sum(compounds) / n, 4),
        "pos": round(sum(pos_list) / n, 4),
        "neu": round(sum(neu_list) / n, 4),
        "neg": round(sum(neg_list) / n, 4),
    }


def claude_extract_themes(client: anthropic.Anthropic, brand: str, texts: list[str], prompt_template: str) -> dict:
    """Call Claude with a batch of texts and return parsed JSON themes."""
    batch = texts[:CLAUDE_BATCH_SIZE]
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(batch))

    category = get_brand_category(brand)
    prompt = (
        prompt_template
        .replace("{{brand}}", brand)
        .replace("{{category}}", category)
        .replace("{{text_items}}", numbered)
    )

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        print(f"    Claude error for {brand}: {e}")
        return {}


def run():
    os.makedirs(DATA_PROCESSED, exist_ok=True)

    # Load raw data
    reddit_path = os.path.join(DATA_RAW, "reddit_raw.csv")
    youtube_path = os.path.join(DATA_RAW, "youtube_raw.csv")
    reddit_df = pd.read_csv(reddit_path) if os.path.exists(reddit_path) else pd.DataFrame()
    youtube_df = pd.read_csv(youtube_path) if os.path.exists(youtube_path) else pd.DataFrame()

    prompt_template = load_prompt_template()
    analyzer = SentimentIntensityAnalyzer()
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    summary_rows = []

    for brand in ALL_BRANDS:
        print(f"  Sentiment: {brand}")
        texts = load_text_for_brand(brand, reddit_df, youtube_df)

        if not texts:
            print(f"    No text found — skipping")
            continue

        vader = vader_score_texts(texts, analyzer)
        themes_data = claude_extract_themes(client, brand, texts, prompt_template)

        # Flatten themes to a string for CSV storage
        top_themes_str = json.dumps(themes_data.get("top_themes", []))
        purchase_channels = "|".join(themes_data.get("purchase_channels_mentioned", []))
        seasonality = "|".join(themes_data.get("seasonality_mentions", []))
        unmet_needs = "|".join(themes_data.get("unmet_needs", []))

        summary_rows.append({
            "brand": brand,
            "text_count": len(texts),
            "vader_compound": vader["compound"],
            "vader_pos": vader["pos"],
            "vader_neu": vader["neu"],
            "vader_neg": vader["neg"],
            "claude_overall_sentiment": themes_data.get("overall_sentiment", ""),
            "claude_positive_pct": themes_data.get("sentiment_breakdown", {}).get("positive_pct", 0),
            "claude_neutral_pct": themes_data.get("sentiment_breakdown", {}).get("neutral_pct", 0),
            "claude_negative_pct": themes_data.get("sentiment_breakdown", {}).get("negative_pct", 0),
            "top_themes_json": top_themes_str,
            "purchase_channels": purchase_channels,
            "seasonality_mentions": seasonality,
            "unmet_needs": unmet_needs,
        })
        print(f"    → {len(texts)} texts | VADER {vader['compound']:.3f} | Claude: {themes_data.get('overall_sentiment', 'n/a')}")

    output_path = os.path.join(DATA_PROCESSED, "brand_sentiment_summary.csv")
    if summary_rows:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"\nSaved {len(summary_rows)} rows → {output_path}")


if __name__ == "__main__":
    run()
