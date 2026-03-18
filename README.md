# CA Healthy Beverage Market Intelligence

> For full project details, see `Project_Summary_v3.docx`.

---

## Project Objectives

Identify the **top 10 healthy beverage brands in California** (Kombucha & Plant-Based Milks) using:
- 5 free data sources
- A 7-signal composite scoring model

Outputs feed a Streamlit dashboard, a growth forecaster, and an automated monthly reporting pipeline.

---

## Tools

### Data Sources
| Tool | Purpose |
|------|---------|
| Arctic Shift (Reddit) | Brand mentions, community discussion |
| Pytrends | Search demand, seasonality, CA geo breakdown |
| SerpAPI | Online vs. in-store purchase signals |
| YouTube Data API | Video reviews, comment sentiment |
| Wikimedia API | Brand momentum via Wikipedia pageviews |

### Analysis & AI
| Tool | Purpose |
|------|---------|
| VADER Sentiment | Per-row local sentiment scoring |
| Claude API (Anthropic) | Sentiment themes, callouts, forecasting, QA |

### Infrastructure
| Tool | Purpose |
|------|---------|
| Streamlit Cloud | Dashboard hosting, monthly refresh |
| Google Sheets / Supabase | Time-series data storage |
| GitHub Actions | Monthly pipeline automation |
| Gmail MCP | Automated monthly digest email |

---

## Phases

| # | Name | Status |
|---|------|--------|
| 1 | Researcher Agent | Active |
| 2 | Dashboard Builder | Planned |
| 3 | Forecaster | Planned |
| 4 | Pipeline + Automation | Planned |

---

## How to Run

**Phase 1 — Full pipeline:**
```bash
python run_phase1.py
```

**Phase 1 — Individual scripts (run in order):**
```bash
python phases/phase1_researcher/01_reddit_scraper.py
python phases/phase1_researcher/02_trends_scraper.py
python phases/phase1_researcher/03_serp_scraper.py
python phases/phase1_researcher/04_youtube_scraper.py
python phases/phase1_researcher/05_wikimedia_scraper.py
python phases/phase1_researcher/06_sentiment_analyzer.py
python phases/phase1_researcher/07_brand_scorer.py
```

**Tests:**
```bash
pytest tests/
```

---

## Scoring Model

Weights are configurable in `config/settings.py`.

| Signal | Weight |
|--------|--------|
| Reddit mention volume | 5% |
| Sentiment score (Reddit + YouTube) | 20% |
| Google Trends avg interest | 20% |
| Google Trends momentum | 15% |
| SerpAPI purchase presence | 15% |
| YouTube engagement signal | 15% |
| Wikimedia pageview momentum | 10% |
