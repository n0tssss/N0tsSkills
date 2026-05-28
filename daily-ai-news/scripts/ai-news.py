#!/usr/bin/env python3
"""
AI News Aggregator — focused on AI models, tools, and technology.
Fetches from curated RSS/API sources, deduplicates, outputs raw articles for LLM processing.
Supports incremental fetching: only articles since last run.
"""

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request

BEIJING_TZ = timezone(timedelta(hours=8))
TRACKING_FILE = os.path.expanduser("~/.hermes/data/ai-news-seen.json")
USER_AGENT = "Mozilla/5.0 (compatible; HermesAgent/1.0)"
FETCH_TIMEOUT = 15

FEEDS = [
    # ── Official model blogs (first-hand AI news) ──
    {"name": "OpenAI Blog",        "url": "https://openai.com/blog/rss.xml",                        "lang": "en"},
    {"name": "Google AI Blog",     "url": "https://feeds.feedburner.com/blogspot/gJZg",             "lang": "en"},

    # ── AI tech news ──
    {"name": "The Verge AI",       "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "lang": "en"},
    {"name": "The Decoder",        "url": "https://the-decoder.com/feed/",                          "lang": "en"},
    {"name": "TechCrunch AI",      "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "lang": "en"},
    {"name": "VentureBeat AI",     "url": "https://venturebeat.com/category/ai/feed",               "lang": "en"},
    {"name": "Ars Technica AI",    "url": "https://arstechnica.com/tag/ai/feed/",                   "lang": "en"},
    {"name": "MIT Tech Review AI", "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "lang": "en"},

    # ── Research / papers ──
    {"name": "Hugging Face Papers","url": "https://huggingface.co/api/daily_papers",                 "lang": "en", "format": "json"},
    {"name": "arXiv cs.AI",        "url": "https://export.arxiv.org/rss/cs.AI",                    "lang": "en"},
    {"name": "arXiv cs.CL",        "url": "https://export.arxiv.org/rss/cs.CL",                    "lang": "en"},

    # ── AI roundups ──
    {"name": "Last Week in AI",    "url": "https://lastweekin.ai/feed/",                            "lang": "en"},
    {"name": "Synced Review",      "url": "https://syncedreview.com/feed/",                         "lang": "en"},
]


# ── Feed fetching & parsing (unchanged) ──

def fetch_url(url):
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def parse_date(date_str):
    if not date_str:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    cleaned = re.sub(r"\s+[A-Z]{2,5}$", "", date_str.strip())
    for fmt in formats:
        try:
            return datetime.strptime(cleaned, fmt)
        except (ValueError, AttributeError):
            continue
    return None


def make_aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_since_last_run(dt, last_run_time):
    """Check if article date is after last run time."""
    if dt is None:
        return True  # Include articles with no date
    dt = make_aware(dt)
    return dt > last_run_time


def is_today(dt):
    """Fallback: check if article is from today."""
    if dt is None:
        return False
    dt = make_aware(dt)
    now = datetime.now(BEIJING_TZ)
    beijing = dt.astimezone(BEIJING_TZ)
    return (beijing.year == now.year and beijing.month == now.month and beijing.day == now.day)


def load_tracking():
    """Load tracking data including seen URLs and last run time."""
    try:
        if os.path.exists(TRACKING_FILE):
            with open(TRACKING_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    urls = set(data.get("urls", []))
                    last_run_str = data.get("last_run")
                    last_run = None
                    if last_run_str:
                        try:
                            last_run = datetime.fromisoformat(last_run_str)
                        except (ValueError, TypeError):
                            pass
                    return urls, last_run
                elif isinstance(data, list):
                    return set(data), None
    except (json.JSONDecodeError, OSError):
        pass
    return set(), None


def save_tracking(urls, last_run_time):
    """Save seen URLs and update last run time."""
    os.makedirs(os.path.dirname(TRACKING_FILE), exist_ok=True)
    with open(TRACKING_FILE, "w") as f:
        json.dump({
            "urls": sorted(list(urls)),
            "last_run": last_run_time.isoformat(),
            "updated": datetime.now(BEIJING_TZ).isoformat()
        }, f, ensure_ascii=False, indent=2)


def parse_json_feed(content, source_name, source_lang):
    articles = []
    if not content:
        return articles
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return articles
    if not isinstance(data, list):
        return articles
    for item in data:
        paper = item.get("paper", {})
        title = paper.get("title", "")
        pid = paper.get("id", "")
        if title and pid:
            url = f"https://arxiv.org/abs/{pid}"
            articles.append({"title": title, "url": url, "date": None, "source": source_name, "lang": source_lang})
    return articles


def parse_feed(content, source_name, source_lang):
    articles = []
    if not content:
        return articles
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return articles

    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # RSS 2.0
    channel = root.find("channel")
    if channel is not None:
        for item in channel.findall("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            date_el = item.find("pubDate") or item.find("{http://purl.org/dc/elements/1.1/}date")
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.text.strip() if link_el is not None and link_el.text else ""
            date_str = date_el.text.strip() if date_el is not None and date_el.text else ""
            if title and link:
                articles.append({"title": title, "url": link, "date": parse_date(date_str), "source": source_name, "lang": source_lang})
    else:
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            link_el = entry.find("atom:link", ns)
            date_el = entry.find("atom:published", ns) or entry.find("atom:updated", ns)
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.get("href", "") if link_el is not None else ""
            date_str = date_el.text.strip() if date_el is not None and date_el.text else ""
            if title and link:
                articles.append({"title": title, "url": link, "date": parse_date(date_str), "source": source_name, "lang": source_lang})
    return articles


def main():
    seen, last_run = load_tracking()
    now = datetime.now(BEIJING_TZ)
    
    # Default: if no last_run, use start of today
    if last_run is None:
        last_run = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    session_urls = set()
    all_articles = []
    errors = []

    for feed in FEEDS:
        content = fetch_url(feed["url"])
        if content is None:
            errors.append(feed["name"])
            continue
        fmt = feed.get("format", "xml")
        if fmt == "json":
            articles = parse_json_feed(content, feed["name"], feed.get("lang", "en"))
        else:
            articles = parse_feed(content, feed["name"], feed.get("lang", "en"))
        for art in articles:
            if art["url"] in seen or art["url"] in session_urls:
                continue
            # Include articles since last run (or today as fallback)
            if is_since_last_run(art["date"], last_run) or is_today(art["date"]):
                all_articles.append(art)
                session_urls.add(art["url"])

    # Save tracking with current time as last_run
    save_tracking(seen | session_urls, now)

    # Output raw JSON for LLM processing
    # Convert dates to ISO strings for JSON serialization
    serializable = []
    for art in all_articles:
        a = dict(art)
        if isinstance(a.get("date"), datetime):
            a["date"] = a["date"].isoformat()
        serializable.append(a)

    output = {
        "fetch_time": now.strftime("%Y-%m-%d %H:%M"),
        "last_run": last_run.strftime("%Y-%m-%d %H:%M"),
        "count": len(all_articles),
        "articles": serializable,
        "errors": errors,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
