# CLAUDE.md — CA Healthy Beverage Market Intelligence


---

## Project Overview
Identifies the top 10 healthy beverage brands in California (Kombucha & Plant-Based Milks) using 5 free data sources and a 7-signal composite scoring model. Outputs feed a Streamlit dashboard, growth forecaster, and automated monthly pipeline.

---

## Tech Stack

| Tool | Phase | Purpose |
|------|-------|---------|
| Arctic Shift | 1 | Brand mentions, community discussion |
| Pytrends | 1 | Search demand, seasonality, CA geo breakdown |
| SerpAPI | 1 | Online vs. in-store purchase signals |
| YouTube Data API | 1 | Video reviews, comment sentiment |
| Wikimedia API | 1 | Brand momentum via Wikipedia pageviews |
| VADER Sentiment | 1 | Per-row sentiment scoring (local, free) |
| Claude API (Anthropic) | All | Sentiment themes, callouts, forecasting, QA |
| Python + Pandas | All | Data cleaning, scoring, CSV export |
| Streamlit Cloud | 2 | Dashboard hosting, monthly refresh |
| Google Sheets / Supabase | 3 | Time-series data storage |
| GitHub Actions | 4 | Monthly pipeline automation |
| Gmail MCP | 4 | Automated monthly digest email |

---

## Core Rules

### ❌ Hard Rules — No Exceptions
- **No** read or write to `.env`
- **No** write to `data/raw/` — scrapers only
- **No** overwrite `data/output/top10_validated.csv` — manually reviewed final output
- **No** file deletion — suggest to user instead
- **No** `git clone`, `curl`, `wget`, `pip download`, or any external download
- **No** access outside `beverage_intel/` — current directory only
- **No** access to `project_information/`

### ⚠️ Ask Before Acting
- **Any edit to an existing file** — state file path, change, and reason; wait for approval
- **Any new library not in `requirements.txt`** — state name, purpose, and justification; wait for approval

### ✅ Permitted Without Approval
- Read any file within `beverage_intel/` except `.env` and `project_information/`
- Write to: `config/`, `phases/`, `prompts/`, `tests/`, `notebooks/`, `logs/`, `data/processed/`, `data/output/top10_brands.csv`
- Create new files in permitted directories
- Read-only bash: `ls`, `cat`, `grep`, `find`, `pytest`, `python <script>`

### Scoring Model (7 signals — configurable in `config/settings.py`)
| Signal | Weight |
|--------|--------|
| Reddit mention volume | 5% |
| Sentiment score (Reddit + YouTube) | 20% |
| Google Trends avg interest | 20% |
| Google Trends momentum | 15% |
| SerpAPI purchase presence | 15% |
| YouTube engagement signal | 15% |
| Wikimedia pageview momentum | 10% |

### Phase Overview
| # | Name | Weeks | Status |
|---|------|-------|--------|
| 1 | Researcher Agent | 1–4 | **ACTIVE** |
| 2 | Dashboard Builder | 5–10 | Planned |
| 3 | Forecaster | 11–14 | Planned |
| 4 | Pipeline + Automation | 15–18 | Planned |

### Code Style
- **Comments:** One line — state what and why; no narrative
- **Organization:** `imports → constants → helpers → main logic`
- **Secrets:** `os.getenv()` only — never hardcoded
- **CSV writes:** `utf-8`, `index=False`
- **Logging:** Write to `logs/` with timestamps; no bare `print()` in production
- **Error handling:** `try/except` all API calls; log failure context before re-raising
- **Claude JSON:** Strip markdown fences before `json.loads()`; validate keys before use

---

## Key Commands

```bash
# Phase 1 entry point
python run_phase1.py

# Run individual scripts in order
python phases/phase1_researcher/01_reddit_scraper.py
python phases/phase1_researcher/02_trends_scraper.py
python phases/phase1_researcher/03_serp_scraper.py
python phases/phase1_researcher/04_youtube_scraper.py
python phases/phase1_researcher/05_wikimedia_scraper.py
python phases/phase1_researcher/06_sentiment_analyzer.py
python phases/phase1_researcher/07_brand_scorer.py

# Run tests
pytest tests/
```

---

## Architecture Pointers
- **File locations & folder structure** → see `Project_folder_structure.txt`
- **Project details, phase breakdown, brand universe, risks & costs** → see `Project_Summary_v3.docx`
