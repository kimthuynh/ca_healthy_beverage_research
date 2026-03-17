"""
Keyword lists for all data sources.
Brand dicts (name → search variants) are used by Reddit, YouTube, and SERP scrapers.
Source-specific lists below tune queries and signal detection per scraper.
"""

# ── Brand Universe ─────────────────────────────────────────────────────────────
# Dict structure required by 01_reddit_scraper, 03_serp_scraper, 04_youtube_scraper,
# 06_sentiment_analyzer, 07_brand_scorer — do not change to lists.

KOMBUCHA_BRANDS = {
    "GT's Living Foods":  ["GT's kombucha", "GTs kombucha", "GT's living foods", "synergy kombucha"],
    "Health-Ade":         ["health-ade kombucha", "health ade kombucha", "healthade"],
    "Brew Dr. Kombucha":  ["brew dr kombucha", "brew doctor kombucha"],
    "Humm Kombucha":      ["humm kombucha"],
    "LIVE Soda Kombucha": ["live soda kombucha", "live kombucha soda"],
    "Rowdy Mermaid":      ["rowdy mermaid kombucha", "rowdy mermaid adaptogen"],
    "Revive Kombucha":    ["revive kombucha", "revive kombucha petaluma"],
    "Wild Tonic":         ["wild tonic kombucha", "wild tonic jun kombucha"],
}

PLANT_MILK_BRANDS = {
    "Oatly":           ["oatly oat milk", "oatly barista", "oatly milk"],
    "Califia Farms":   ["califia farms", "califia oat milk", "califia almond milk"],
    "Ripple Foods":    ["ripple pea milk", "ripple plant milk", "ripple foods"],
    "Elmhurst 1925":   ["elmhurst oat milk", "elmhurst nut milk", "elmhurst 1925"],
    "Malk Organics":   ["malk oat milk", "malk almond milk", "malk organics"],
    "Three Trees":     ["three trees almond milk", "three trees plant milk"],
    "Forager Project": ["forager oat milk", "forager cashew milk", "forager project"],
    "Silk":            ["silk oat milk", "silk almond milk", "silk plant milk"],
    "So Delicious":    ["so delicious coconut milk", "so delicious dairy free"],
    "MUSH":            ["mush oat milk", "mush overnight oats", "mush drink"],
    "New Barn Organics": ["new barn almond milk", "new barn organics"],
    "Harmless Harvest":  ["harmless harvest coconut water", "harmless harvest"],
}

ALL_BRANDS = {**KOMBUCHA_BRANDS, **PLANT_MILK_BRANDS}


# ── 1. Apify Reddit Scraper ────────────────────────────────────────────────────
# TARGET_SUBREDDITS: passed directly to Apify actor
# REDDIT_CONTEXT_TERMS: appended to brand name to build search queries

TARGET_SUBREDDITS = [
    "Kombucha",
    "PlantBasedDiet",
    "veganfoodporn",
    "vegan",
    "Fitness",
    "loseit",
    "nutrition",
    "GutHealth",
    "BuyItForLife",
    "ZeroWaste",
]

REDDIT_CONTEXT_TERMS = [
    "review",
    "taste",
    "where to buy",
]


# ── 2. Pytrends — Google Trends ───────────────────────────────────────────────
# TRENDS_CATEGORY_TERMS: category-level CA trend comparisons (max 5 per request)
# TRENDS_MOMENTUM_MODIFIERS: appended to brand name to track purchase-intent shifts

TRENDS_CATEGORY_TERMS = [
    "kombucha",
    "fermented drink",
    "probiotic drink",
    "gut health drink",
    "oat milk",
    "plant based milk",
    "dairy free milk",
    "nut milk",
    "pea milk",
    "coconut milk",
    "healthy beverage",
]

TRENDS_MOMENTUM_MODIFIERS = [
    "best",
    "new",
    "buy",
    "near me",
    "review",
    "where to buy",
    "discount",
    "coupon",
    "sale",
]


# ── 3. SerpAPI — Online Purchase Signals ──────────────────────────────────────
# SERP_QUERY_TEMPLATES: used by scraper to build per-brand search queries
# SERP_PURCHASE_TERMS / SERP_INSTORE_TERMS: used by classify_channel() to label results

SERP_QUERY_TEMPLATES = [
    "{brand} buy online",
    "{brand} where to buy California",
    "{brand} store near me",
]

SERP_PURCHASE_TERMS = [
    "buy online",
    "where to buy",
    "delivery",
    "subscribe",
    "amazon",
    "instacart",
    "whole foods delivery",
    "walmart",
    "target",
    "thrive market",
    "shop",
    "order",
    "price",
    "case pack",
    "bulk",
]

SERP_INSTORE_TERMS = [
    "near me",
    "store locator",
    "whole foods",
    "sprouts",
    "trader joe",
    "safeway",
    "kroger",
    "costco",
    "total wine",
    "natural grocery",
]


# ── 4. YouTube Data API ────────────────────────────────────────────────────────
# YOUTUBE_QUERY_TEMPLATES: used by scraper with .format(brand=brand)
# YOUTUBE_COMMENT_SIGNALS: used during sentiment pass to flag high-signal comments

YOUTUBE_QUERY_TEMPLATES = [
    "{brand} review",
    "{brand} taste test",
    "{brand} honest review",
    "{brand} is it worth it",
    "{brand} healthy or not",
    "{brand} unboxing",
    "{brand} vs",
    "{brand} recipe",
    "{brand} ranking",
    "{brand} best flavor",
    "{brand} gut health",
    "{brand} dietitian review",
    "{brand} nutritionist opinion",
]

YOUTUBE_COMMENT_SIGNALS = [
    "love",
    "hate",
    "disgusting",
    "addicted",
    "switched",
    "stopped buying",
    "best",
    "worst",
    "expensive",
    "affordable",
    "found at",
    "whole foods",
    "amazon",
    "side effect",
    "bloated",
    "energy",
    "sugar",
    "ingredients",
]


# ── 5. Wikimedia API — Brand Momentum ─────────────────────────────────────────
# Exact Wikipedia article titles as they appear on Wikipedia (spaces, not underscores)

WIKIPEDIA_ARTICLE_TITLES = {
    # Kombucha brands
    "GT's Living Foods":  "GT's Living Foods",
    "Health-Ade":         "Health-Ade",
    "Brew Dr. Kombucha":  "Brew Dr. Kombucha",
    "Humm Kombucha":      "Humm Kombucha",
    "LIVE Soda Kombucha": "LIVE Soda",
    "Rowdy Mermaid":      "Rowdy Mermaid Kombucha",
    "Revive Kombucha":    "Revive Kombucha",
    "Wild Tonic":         "Wild Tonic",
    # Plant-based milks
    "Oatly":             "Oatly",
    "Califia Farms":     "Califia Farms",
    "Ripple Foods":      "Ripple Foods",
    "Elmhurst 1925":     "Elmhurst 1925",
    "Malk Organics":     "Malk Organics",
    "Three Trees":       "Three Trees (company)",
    "Forager Project":   "Forager Project",
    "Silk":              "Silk (brand)",
    "So Delicious":      "So Delicious",
    "MUSH":              "MUSH (brand)",
    "New Barn Organics": "New Barn Organics",
    "Harmless Harvest":  "Harmless Harvest",
}

# Category-level pages for macro trend context
WIKIPEDIA_CATEGORY_PAGES = [
    "Kombucha",
    "Plant milk",
    "Oat milk",
    "Fermented beverages",
    "Probiotic",
    "Dairy alternative",
]
