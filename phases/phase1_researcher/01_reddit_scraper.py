"""
01_reddit_scraper.py
Pull Reddit posts + comments for all 20 brands via Arctic Shift API.
Scope: 20 brands x 3 queries x 10 subreddits x 20 posts x 20 comments.
No API key required. Rate limit respected via X-RateLimit-Remaining header.
Output: data/raw/reddit_raw.csv
"""

import csv
import os
import time

import requests

from config.settings import (
    DATA_RAW,
    REDDIT_MAX_POSTS, REDDIT_DATE_FROM, REDDIT_DATE_TO,
)
from config.keywords import ALL_BRANDS, TARGET_SUBREDDITS, REDDIT_CONTEXT_TERMS

BASE_URL = "https://arctic-shift.photon-reddit.com"
HEADERS = {"User-Agent": "BeverageIntelProject/1.0 (research@internal)"}
MAX_COMMENTS_PER_POST = 50
SLEEP_BETWEEN_REQUESTS = 1.5  # stay well under rate limit


def check_rate_limit(response: requests.Response):
    """Slow down if rate limit is running low."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining and int(remaining) < 10:
        print("    Rate limit low — sleeping 10s")
        time.sleep(10)


def search_posts(query: str, subreddit: str) -> list[dict]:
    """Search posts in one subreddit for a keyword query."""
    params = {
        "title":     query,      # searches post titles; "q" is not a valid param
        "subreddit": subreddit,
        "after":     REDDIT_DATE_FROM,
        "before":    REDDIT_DATE_TO,
        "limit":     min(REDDIT_MAX_POSTS, 100),  # API max is 100
        "sort":      "desc",
        "sort_type": "created_utc",
    }
    try:
        resp = requests.get(f"{BASE_URL}/api/posts/search", params=params,
                            headers=HEADERS, timeout=15)
        resp.raise_for_status()
        check_rate_limit(resp)
        return resp.json().get("data", [])
    except Exception as e:
        print(f"      Post search error ({subreddit} / '{query}'): {e}")
        return []


def fetch_comments(post_id: str) -> list[dict]:
    """Fetch top comments for a post by its ID."""
    params = {
        "link_id":   post_id,
        "limit":     MAX_COMMENTS_PER_POST,
        "sort":      "desc",
        "sort_type": "created_utc",
    }
    try:
        resp = requests.get(f"{BASE_URL}/api/comments/search", params=params,
                            headers=HEADERS, timeout=15)
        resp.raise_for_status()
        check_rate_limit(resp)
        return resp.json().get("data", [])
    except Exception as e:
        print(f"      Comment fetch error (post {post_id}): {e}")
        return []


def build_queries(brand: str) -> list[str]:
    """Build 3 queries: primary brand variant + each REDDIT_CONTEXT_TERMS entry."""
    primary = ALL_BRANDS.get(brand, [brand])[0]
    # Produces: "{primary} review", "{primary} taste", "{primary} where to buy"
    return [f"{primary} {term}" for term in REDDIT_CONTEXT_TERMS]


def run():
    os.makedirs(DATA_RAW, exist_ok=True)
    output_path = os.path.join(DATA_RAW, "reddit_raw.csv")

    fieldnames = ["brand", "query", "post_id", "subreddit", "title", "text",
                  "score", "num_comments", "url", "created_utc", "type"]

    all_rows = []

    for brand in ALL_BRANDS:
        print(f"  Reddit: {brand}")
        queries = build_queries(brand)
        seen_post_ids = set()
        brand_rows = []

        for query in queries:
            for subreddit in TARGET_SUBREDDITS:
                posts = search_posts(query, subreddit)

                for post in posts:
                    post_id = post.get("id", "")
                    if not post_id or post_id in seen_post_ids:
                        continue
                    seen_post_ids.add(post_id)

                    brand_rows.append({
                        "brand": brand,
                        "query": query,
                        "post_id": post_id,
                        "subreddit": post.get("subreddit", subreddit),
                        "title": post.get("title", ""),
                        "text": post.get("selftext", ""),
                        "score": post.get("score", 0),
                        "num_comments": post.get("num_comments", 0),
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "created_utc": post.get("created_utc", ""),
                        "type": "post",
                    })

                    # Fetch comments for posts with meaningful engagement
                    if post.get("num_comments", 0) > 2:
                        comments = fetch_comments(post_id)
                        for comment in comments:
                            body = comment.get("body", "").strip()
                            if not body or body in ("[deleted]", "[removed]"):
                                continue
                            brand_rows.append({
                                "brand": brand,
                                "query": query,
                                "post_id": post_id,
                                "subreddit": post.get("subreddit", subreddit),
                                "title": "",
                                "text": body,
                                "score": comment.get("score", 0),
                                "num_comments": 0,
                                "url": "",
                                "created_utc": comment.get("created_utc", ""),
                                "type": "comment",
                            })
                        time.sleep(SLEEP_BETWEEN_REQUESTS)

                time.sleep(SLEEP_BETWEEN_REQUESTS)

        all_rows.extend(brand_rows)
        print(f"    → {len(brand_rows)} items ({len(seen_post_ids)} posts)")

    if not all_rows:
        print("No data collected.")
        return

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nSaved {len(all_rows)} rows → {output_path}")


if __name__ == "__main__":
    run()
