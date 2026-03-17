"""
04_youtube_scraper.py
Pull video metadata + comments per brand via YouTube Data API v3.
Outputs: data/raw/youtube_raw.csv
         data/processed/youtube_summary.csv
"""

import csv
import os

from googleapiclient.discovery import build

from config.settings import (
    YOUTUBE_API_KEY, DATA_RAW, DATA_PROCESSED,
    YOUTUBE_MAX_RESULTS, YOUTUBE_MAX_COMMENTS,
    YOUTUBE_ORDER, YOUTUBE_PUBLISHED_AFTER,
)
from config.keywords import ALL_BRANDS, YOUTUBE_QUERY_TEMPLATES, YOUTUBE_COMMENT_SIGNALS


def get_youtube_client():
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def search_videos(client, query: str) -> list[dict]:
    """Search YouTube for videos matching query, return video metadata."""
    try:
        response = client.search().list(
            q=query,
            part="id,snippet",
            type="video",
            maxResults=YOUTUBE_MAX_RESULTS,
            order=YOUTUBE_ORDER,
            publishedAfter=YOUTUBE_PUBLISHED_AFTER,
            relevanceLanguage="en",
        ).execute()
        return response.get("items", [])
    except Exception as e:
        print(f"    YouTube search error for '{query}': {e}")
        return []


def get_video_stats(client, video_ids: list[str]) -> dict:
    """Batch fetch view/like/comment counts for up to 50 video IDs."""
    if not video_ids:
        return {}
    try:
        response = client.videos().list(
            part="statistics",
            id=",".join(video_ids),
        ).execute()
        return {item["id"]: item.get("statistics", {}) for item in response.get("items", [])}
    except Exception as e:
        print(f"    YouTube stats error: {e}")
        return {}


def get_comments(client, video_id: str) -> list[str]:
    """Fetch top-level comments for a video."""
    try:
        response = client.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=YOUTUBE_MAX_COMMENTS,
            order="relevance",
            textFormat="plainText",
        ).execute()
        return [
            item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            for item in response.get("items", [])
        ]
    except Exception:
        return []  # comments disabled or quota hit


def run():
    os.makedirs(DATA_RAW, exist_ok=True)
    os.makedirs(DATA_PROCESSED, exist_ok=True)

    client = get_youtube_client()
    raw_rows = []
    summary_rows = []

    for brand in ALL_BRANDS:
        print(f"  YouTube: {brand}")
        queries = [t.format(brand=brand) for t in YOUTUBE_QUERY_TEMPLATES[:2]]

        seen_video_ids = set()
        brand_videos = []

        for query in queries:
            items = search_videos(client, query)
            for item in items:
                vid_id = item["id"].get("videoId")
                if not vid_id or vid_id in seen_video_ids:
                    continue
                seen_video_ids.add(vid_id)
                brand_videos.append({
                    "video_id": vid_id,
                    "title": item["snippet"].get("title", ""),
                    "channel": item["snippet"].get("channelTitle", ""),
                    "published_at": item["snippet"].get("publishedAt", ""),
                    "query": query,
                })

        # Batch fetch stats
        stats_map = get_video_stats(client, list(seen_video_ids))

        total_views = 0
        total_comments_fetched = 0
        comment_texts = []

        for video in brand_videos:
            vid_id = video["video_id"]
            stats = stats_map.get(vid_id, {})
            view_count = int(stats.get("viewCount", 0))
            comment_count = int(stats.get("commentCount", 0))
            total_views += view_count
            total_comments_fetched += comment_count

            # Fetch actual comment text for top videos only (saves quota)
            if view_count > 1000:
                comments = get_comments(client, vid_id)
            else:
                comments = []

            for comment_text in comments:
                comment_texts.append(comment_text)
                text_lower = comment_text.lower()
                flagged = [s for s in YOUTUBE_COMMENT_SIGNALS if s in text_lower]
                raw_rows.append({
                    "brand": brand,
                    "video_id": vid_id,
                    "video_title": video["title"],
                    "channel": video["channel"],
                    "published_at": video["published_at"],
                    "view_count": view_count,
                    "comment_count": comment_count,
                    "text": comment_text,
                    "flagged_signals": "|".join(flagged),
                    "type": "comment",
                })

            # Also add video title as a row for sentiment analysis
            raw_rows.append({
                "brand": brand,
                "video_id": vid_id,
                "video_title": video["title"],
                "channel": video["channel"],
                "published_at": video["published_at"],
                "view_count": view_count,
                "comment_count": comment_count,
                "text": video["title"],
                "flagged_signals": "",
                "type": "video_title",
            })

        # Engagement score: log-normalized view total (0-100)
        import math
        engagement_score = round(min(math.log10(total_views + 1) / 7 * 100, 100), 2) if total_views else 0

        summary_rows.append({
            "brand": brand,
            "video_count": len(brand_videos),
            "total_views": total_views,
            "total_comments": total_comments_fetched,
            "comment_texts_collected": len(comment_texts),
            "engagement_score": engagement_score,
        })
        print(f"    → {len(brand_videos)} videos | {total_views:,} views | score {engagement_score}")

    # Save raw
    raw_path = os.path.join(DATA_RAW, "youtube_raw.csv")
    if raw_rows:
        with open(raw_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=raw_rows[0].keys())
            writer.writeheader()
            writer.writerows(raw_rows)
        print(f"\nSaved {len(raw_rows)} rows → {raw_path}")

    # Save summary
    summary_path = os.path.join(DATA_PROCESSED, "youtube_summary.csv")
    if summary_rows:
        with open(summary_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
            writer.writeheader()
            writer.writerows(summary_rows)
        print(f"Saved {len(summary_rows)} rows → {summary_path}")


if __name__ == "__main__":
    run()
