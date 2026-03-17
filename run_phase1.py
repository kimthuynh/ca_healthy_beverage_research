"""
run_phase1.py
Phase 1 orchestrator — runs all 7 scripts sequentially.
Usage: python run_phase1.py [--skip SCRIPT_NUM] [--only SCRIPT_NUM]
"""

import argparse
import importlib.util
import os
import sys
import time
from pathlib import Path


PHASE1_DIR = Path("phases/phase1_researcher")

SCRIPTS = [
    (1, "01_reddit_scraper",    "Reddit posts + comments via Arctic Shift API"),
    (2, "02_trends_scraper",    "Google Trends CA via Pytrends"),
    (3, "03_serp_scraper",      "Purchase signals via SerpAPI"),
    (4, "04_youtube_scraper",   "Video reviews + comments via YouTube API"),
    (5, "05_wikimedia_scraper", "Brand pageviews via Wikimedia"),
    (6, "06_sentiment_analyzer","VADER + Claude theme extraction"),
    (7, "07_brand_scorer",      "Composite scoring → Top 10"),
]


def load_and_run(script_name: str):
    """Dynamically import and run a phase1 script."""
    script_path = PHASE1_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.run()


def check_env():
    """Warn on missing .env keys before starting."""
    required = ["APIFY_TOKEN", "YOUTUBE_API_KEY", "SERPAPI_KEY", "ANTHROPIC_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"[WARNING] Missing env vars: {', '.join(missing)}")
        print("  → Some scripts may fail. Check your .env file.\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Run Phase 1 pipeline")
    parser.add_argument("--skip", type=int, nargs="+", metavar="N",
                        help="Script numbers to skip (e.g. --skip 1 2)")
    parser.add_argument("--only", type=int, nargs="+", metavar="N",
                        help="Run only these script numbers (e.g. --only 6 7)")
    return parser.parse_args()


def main():
    args = parse_args()
    check_env()

    # Ensure data directories exist
    for d in ["data/raw", "data/processed", "data/output", "logs"]:
        os.makedirs(d, exist_ok=True)

    to_run = SCRIPTS
    if args.only:
        to_run = [s for s in SCRIPTS if s[0] in args.only]
    elif args.skip:
        to_run = [s for s in SCRIPTS if s[0] not in args.skip]

    print("=" * 55)
    print("  BEVERAGE INTEL — PHASE 1 PIPELINE")
    print("=" * 55)
    print(f"  Scripts to run: {[s[0] for s in to_run]}\n")

    results = []
    total_start = time.time()

    for num, name, description in to_run:
        print(f"\n[{num}/7] {description}")
        print("-" * 45)
        start = time.time()
        try:
            load_and_run(name)
            elapsed = round(time.time() - start, 1)
            results.append((num, name, "OK", elapsed))
            print(f"  ✓ Done in {elapsed}s")
        except Exception as e:
            elapsed = round(time.time() - start, 1)
            results.append((num, name, f"FAILED: {e}", elapsed))
            print(f"  ✗ FAILED: {e}")
            print("  → Continuing to next script...")

    total_elapsed = round(time.time() - total_start, 1)

    print("\n" + "=" * 55)
    print("  PHASE 1 SUMMARY")
    print("=" * 55)
    for num, name, status, elapsed in results:
        icon = "✓" if status == "OK" else "✗"
        print(f"  {icon} [{num}] {name:<30} {elapsed:>6}s  {'' if status == 'OK' else status}")

    failed = [r for r in results if r[2] != "OK"]
    print(f"\n  Total time: {total_elapsed}s | Passed: {len(results)-len(failed)} | Failed: {len(failed)}")

    if not failed:
        print("\n  Phase 1 complete. Check data/output/top10_brands.csv")
        print("  Next: manually review → save as top10_validated.csv → start Phase 2")
    else:
        print(f"\n  {len(failed)} script(s) failed. Review errors above and re-run with --only <num>")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
