"""
Claude callout generator for dashboard panels.
Caches results by data hash — only re-calls API when data changes.
"""

import hashlib
import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# Load .env from project root regardless of where the script is called from
# Project root = 2 levels up from phases/phase2_dashboard/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

CACHE_PATH = PROJECT_ROOT / "data" / "processed" / "callout_cache.json"
PROMPT_PATH = PROJECT_ROOT / "prompts" / "insight_narrator.md"

PANEL_LABELS = [
    "brand_rankings",
    "sentiment_heatmap",
    "trends_chart",
    "youtube_engagement",
    "wikimedia_momentum",
    "purchase_channels",
]


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def _hash_data(data_str: str) -> str:
    return hashlib.md5(data_str.encode()).hexdigest()


def _load_system_prompt() -> str:
    with open(PROMPT_PATH, "r") as f:
        return f.read()


def _call_claude(panel: str, data_str: str) -> str:
    """Call Claude API and return plain-text callout."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    system_prompt = _load_system_prompt()
    user_message = f'Data: "{data_str}"\nPanel context: "{panel}"'

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text.strip()


def get_callout(panel: str, data_str: str, force_refresh: bool = False) -> str:
    """
    Return cached callout or generate a new one.
    Keyed by panel + md5 hash of data_str.
    """
    cache = _load_cache()
    data_hash = _hash_data(data_str)
    cache_key = f"{panel}::{data_hash}"

    if not force_refresh and cache_key in cache:
        return cache[cache_key]

    callout = _call_claude(panel, data_str)
    cache[cache_key] = callout
    _save_cache(cache)
    return callout


def get_all_callouts(panel_data: dict[str, str], force_refresh: bool = False) -> dict[str, str]:
    """
    Generate callouts for all panels.
    panel_data: {panel_name: data_string}
    Returns: {panel_name: callout_text}
    """
    return {
        panel: get_callout(panel, data_str, force_refresh)
        for panel, data_str in panel_data.items()
    }
