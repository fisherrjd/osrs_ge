import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests
from sqlmodel import Session, SQLModel, create_engine, select

from api.schemas.news_models import CategoryType, NewsItem, SourceType

# API URLs
OSRS_RSS_URL = "https://secure.runescape.com/m=news/latest_news.rss?oldschool=true"
REDDIT_API_URL = "https://www.reddit.com/r/2007scape/top.json?t=week"

HEADERS = {
    "User-Agent": "OSRS-GE-Tracker/1.0 (contact: dev@jade.rip)",
}

# Reddit requires a more specific user agent
REDDIT_HEADERS = {
    "User-Agent": "OSRS-GE-Tracker/1.0 (by /u//Ok-Jellyfish-8658/)",
}

DB_FILE = os.getenv("DB_FILE", "sqlite:///news.db")

engine = create_engine(DB_FILE)
SQLModel.metadata.create_all(engine)


def parse_osrs_category(title: str, summary: str) -> CategoryType:
    """Determine category from OSRS blog post title/summary."""
    title_lower = title.lower()
    summary_lower = summary.lower() if summary else ""

    if "patch" in title_lower or "hotfix" in title_lower:
        return CategoryType.PATCH
    elif "update" in title_lower or "changelog" in title_lower:
        return CategoryType.UPDATE
    elif (
        "event" in title_lower
        or "competition" in title_lower
        or "league" in title_lower
    ):
        return CategoryType.EVENT
    elif "community" in summary_lower or "poll" in title_lower:
        return CategoryType.COMMUNITY
    else:
        # Default to UPDATE for official blog posts
        return CategoryType.UPDATE


def fetch_osrs_news() -> list[NewsItem]:
    """Fetch news from OSRS official RSS feed."""
    response = requests.get(OSRS_RSS_URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch OSRS RSS: {response.status_code}")

    root = ET.fromstring(response.content)
    items = []

    # RSS items are under channel/item
    for item_elem in root.findall(".//item"):
        title = item_elem.findtext("title", "")
        link = item_elem.findtext("link", "")
        description = item_elem.findtext("description", "")
        pub_date_str = item_elem.findtext("pubDate", "")
        guid = item_elem.findtext("guid", link)

        # Parse publication date (RFC 2822 format)
        try:
            pub_date = parsedate_to_datetime(pub_date_str)
        except (ValueError, TypeError):
            pub_date = datetime.now(timezone.utc)

        category = parse_osrs_category(title, description)

        item = NewsItem(
            title=title,
            description=description[:500] if description else None,
            source=SourceType.OFFICIAL,
            source_identifier=guid,
            category=category,
            date=pub_date,
            url=link,
        )
        items.append(item)

    return items


def parse_reddit_category(flair: str | None, title: str) -> CategoryType:
    """Determine category from Reddit post flair/title."""
    if flair:
        flair_lower = flair.lower()
        if "news" in flair_lower or "jmod" in flair_lower:
            return CategoryType.UPDATE
        elif "event" in flair_lower:
            return CategoryType.EVENT

    title_lower = title.lower()
    if "update" in title_lower or "patch" in title_lower:
        return CategoryType.PATCH

    return CategoryType.COMMUNITY


def fetch_reddit_news(min_score: int = 100) -> list[NewsItem]:
    """Fetch top posts from r/2007scape."""
    response = requests.get(REDDIT_API_URL, headers=REDDIT_HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch Reddit data: {response.status_code}")

    data = response.json()
    items = []

    for child in data["data"]["children"]:
        post = child["data"]

        # Skip posts below minimum score
        if post.get("score", 0) < min_score:
            continue

        # Skip stickied/pinned posts
        if post.get("stickied", False):
            continue

        # Parse creation date
        created_utc = post.get("created_utc", 0)
        pub_date = datetime.fromtimestamp(created_utc, tz=timezone.utc)

        flair = post.get("link_flair_text")
        category = parse_reddit_category(flair, post["title"])

        # Build Reddit URL
        permalink = post.get("permalink", "")
        url = f"https://www.reddit.com{permalink}" if permalink else post.get("url", "")

        item = NewsItem(
            title=post["title"],
            description=post.get("selftext", "")[:500]
            if post.get("selftext")
            else None,
            source=SourceType.REDDIT,
            source_identifier=post.get("id"),
            category=category,
            date=pub_date,
            url=url,
            upvotes=post.get("score"),
            comments=post.get("num_comments"),
        )
        items.append(item)

    return items


def fetch_all_news() -> list[NewsItem]:
    """Fetch news from all sources."""
    all_items = []

    try:
        osrs_items = fetch_osrs_news()
        all_items.extend(osrs_items)
        print(f"Fetched {len(osrs_items)} items from OSRS blog")
    except Exception as e:
        print(f"Error fetching OSRS news: {e}")

    try:
        reddit_items = fetch_reddit_news()
        all_items.extend(reddit_items)
        print(f"Fetched {len(reddit_items)} items from Reddit")
    except Exception as e:
        print(f"Error fetching Reddit news: {e}")

    return all_items


def update_database(items: list[NewsItem]):
    """Update the database with news items, avoiding duplicates."""
    with Session(engine) as session:
        for item in items:
            # Check if item already exists by URL
            existing = session.exec(
                select(NewsItem).where(NewsItem.url == item.url)
            ).first()

            if existing:
                # Update mutable fields (upvotes, comments for Reddit)
                if item.source == SourceType.REDDIT:
                    existing.upvotes = item.upvotes
                    existing.comments = item.comments
                existing.updated_at = datetime.now(timezone.utc)
                existing.score = existing.calculate_score()
            else:
                # New item - calculate score and add
                item.score = item.calculate_score()
                session.add(item)

        session.commit()


def recalculate_all_scores():
    """Recalculate scores for all items (handles time decay)."""
    with Session(engine) as session:
        items = session.exec(select(NewsItem)).all()
        for item in items:
            item.score = item.calculate_score()
            item.updated_at = datetime.now(timezone.utc)
        session.commit()
        print(f"Recalculated scores for {len(items)} items")


if __name__ == "__main__":
    print("Starting news aggregator...")
    run_count = 0

    while True:
        print(f"\n--- Run #{run_count + 1} ---")

        # Fetch and update news
        items = fetch_all_news()
        if items:
            update_database(items)
            print(f"Database updated with {len(items)} items")

        # Recalculate all scores every run (time decay)
        recalculate_all_scores()

        print("Waiting 30 minutes for next run...")
        run_count += 1
        time.sleep(1800)  # 30 minutes
