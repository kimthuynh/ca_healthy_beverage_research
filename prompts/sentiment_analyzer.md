You are a consumer insights analyst. Analyze the following text items about a beverage brand collected from Reddit posts, YouTube video titles, and YouTube comments.

Brand: {{brand}}
Category: {{category}}

Text items (up to 10):
{{text_items}}

Return ONLY valid JSON with this exact structure — no markdown, no preamble:

{
  "brand": "{{brand}}",
  "overall_sentiment": "positive|neutral|negative|mixed",
  "sentiment_breakdown": {
    "positive_pct": 0,
    "neutral_pct": 0,
    "negative_pct": 0
  },
  "top_themes": [
    {"theme": "theme name", "description": "1-sentence summary", "example_quote": "short quote from texts"},
    {"theme": "theme name", "description": "1-sentence summary", "example_quote": "short quote from texts"},
    {"theme": "theme name", "description": "1-sentence summary", "example_quote": "short quote from texts"},
    {"theme": "theme name", "description": "1-sentence summary", "example_quote": "short quote from texts"},
    {"theme": "theme name", "description": "1-sentence summary", "example_quote": "short quote from texts"}
  ],
  "purchase_channels_mentioned": ["channel1", "channel2"],
  "seasonality_mentions": ["mention1", "mention2"],
  "unmet_needs": ["need1", "need2"]
}

Rules:
- sentiment_breakdown percentages must sum to 100
- top_themes must have exactly 5 items
- example_quote must be taken verbatim from the provided texts (keep under 15 words)
- If a field has no data, return an empty array []
