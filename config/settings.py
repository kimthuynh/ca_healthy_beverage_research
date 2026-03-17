import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
#APIFY_TOKEN = os.getenv("APIFY_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# --- Anthropic ---
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 1500
CLAUDE_BATCH_SIZE = 10  # text items sent per brand per API call

# # --- Apify Reddit Scraper ---
# APIFY_ACTOR_ID = "trudax/reddit-scraper-lite"
# REDDIT_MAX_POSTS = 50       # per brand
# REDDIT_MAX_COMMENTS = 100   # per post
# REDDIT_DATE_FROM = "2025-01-01"
# REDDIT_DATE_TO = "2026-03-31"


# --- Arctic Shift (Reddit) --- no API key required
REDDIT_MAX_POSTS = 50       # per query per subreddit
REDDIT_DATE_FROM = "2025-01-01"
REDDIT_DATE_TO = "2026-03-31"


# --- Pytrends ---
TRENDS_GEO = "US-CA"        # California
TRENDS_TIMEFRAME = "2025-01-01 2026-03-31"
TRENDS_SLEEP_SECONDS = 10   # avoid 429 rate limits
TRENDS_BATCH_SIZE = 5       # max 5 keywords per Pytrends request

# --- SerpAPI ---
SERP_MAX_QUERIES_PER_BRAND = 3   # cap total at 60 calls (20 brands × 3)
SERP_LOCATION = "California, United States"
SERP_NUM_RESULTS = 10

# --- YouTube Data API ---
YOUTUBE_MAX_RESULTS = 10    # videos per query
YOUTUBE_MAX_COMMENTS = 20   # comments per video
YOUTUBE_ORDER = "relevance"
YOUTUBE_PUBLISHED_AFTER = "2025-01-01T00:00:00Z"

# --- Wikimedia ---
WIKIMEDIA_PROJECT = "en.wikipedia"
WIKIMEDIA_ACCESS = "all-access"
WIKIMEDIA_AGENT = "all-agents"
WIKIMEDIA_GRANULARITY = "monthly"
WIKIMEDIA_START = "2025010100"
WIKIMEDIA_END = "2026033100"

# --- Scoring weights (must sum to 1.0) ---
SCORE_WEIGHTS = {
    "reddit_volume":      0.05,
    "sentiment_score":    0.20,
    "trends_avg":         0.20,
    "trends_momentum":    0.15,
    "serp_presence":      0.15,
    "youtube_engagement": 0.15,
    "wikimedia_momentum": 0.10,
}

# --- Paths ---
DATA_RAW = "data/raw"
DATA_PROCESSED = "data/processed"
DATA_OUTPUT = "data/output"
PROMPTS_DIR = "prompts"
