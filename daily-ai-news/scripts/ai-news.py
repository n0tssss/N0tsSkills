#!/usr/bin/env python3
"""
AI News Aggregator v3 — focused on AI model updates & practical tools.
Fetches from curated RSS/API sources + HTML blog/doc pages, with smart filtering.
Only outputs articles that matter: model releases, API changes, developer tools.
"""

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request
from urllib.parse import quote as urlquote

BEIJING_TZ = timezone(timedelta(hours=8))
TRACKING_FILE = os.path.expanduser("~/.hermes/data/ai-news-seen.json")
USER_AGENT = "Mozilla/5.0 (compatible; HermesAgent/1.0)"
FETCH_TIMEOUT = 15

# ── GitHub API config ──
GITHUB_TOKEN_FILE = os.path.expanduser("~/.hermes/.github_token")

# ── Include keywords ──
INCLUDE_KEYWORDS = [
    # Model releases
    "release", "launch", "announce", "introducing", "new model", "update",
    "发布", "上线", "更新", "升级", "推出", "新增", "开源",
    # Model names (international)
    "gpt", "o3", "o4", "claude", "gemini", "llama", "mistral", "grok",
    # Model names (Chinese)
    "deepseek", "qwen", "glm", "baichuan", "yi", "minimax", "step",
    "doubao", "kimi", "hunyuan", "pangu", "spark", "ernie", "mimo",
    "moonshot", "skywork",
    # Tools/API
    "api", "sdk", "tool", "platform", "developer", "pricing", "cursor", "copilot",
    "claude code", "openai codex", "opencode", "kilo code", "mimo code",
    "windsurf", "aider", "continue", "cline", "roo code",
    "mcp", "skill", "plugin", "extension", "agent", "agentic",
    "工具", "平台", "开发者", "定价", "插件", "技能", "智能体",
    # Open source
    "open source", "open-source", "github", "huggingface",
    # Capabilities
    "benchmark", "performance", "context window", "reasoning", "coding",
    "基准", "性能", "上下文", "推理", "编程",
]

# ── Exclude keywords ──
EXCLUDE_KEYWORDS = [
    # Hiring/office
    "hiring", "job", "career", "office", "expansion", "总部",
    "招聘", "职位", "办公", "扩张",
    # Media/opinion
    "podcast", "interview", "opinion", "editorial",
    "播客", "访谈", "观点",
    # Business partnerships
    "sponsor", "partner", "collaboration", "生态共建",
    "赞助", "合作伙伴",
    # Enterprise/commercial (过滤纯商业新闻)
    "enterprise", "企业级", "商业化落地",
    # Political
    "president", "minister", "government", "总统", "部长",
    # Ads
    "ads", "advertising", "广告",
]

# ── RSS Feeds ──
RSS_FEEDS = [
    {"name": "OpenAI Blog",        "url": "https://openai.com/blog/rss.xml",                        "lang": "en", "max_articles": 8},
    {"name": "Google AI Blog",     "url": "https://feeds.feedburner.com/blogspot/gJZg",             "lang": "en", "max_articles": 8},
    {"name": "The Verge AI",       "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "lang": "en", "max_articles": 6},
    {"name": "TechCrunch AI",      "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "lang": "en", "max_articles": 6},
    {"name": "VentureBeat AI",     "url": "https://venturebeat.com/category/ai/feed",               "lang": "en", "max_articles": 6},
    {"name": "Hugging Face Papers","url": "https://huggingface.co/api/daily_papers",                 "lang": "en", "format": "json", "max_articles": 6},
]

# ── HTML Blog / Doc Pages ──
HTML_BLOGS = [
    # ── International ──
    {"name": "Anthropic",       "url": "https://www.anthropic.com/news",           "lang": "en", "max_articles": 6,
     "pattern": r'href="(/news/[^"]+)"[^>]*>.*?(?:<h[23][^>]*>([^<]+)</h[23]>|class="[^"]*title[^"]*"[^>]*>([^<]+)<)',
     "dotall": True},
    {"name": "Meta AI",         "url": "https://ai.meta.com/blog/",                "lang": "en", "max_articles": 6,
     "pattern": r'href="(https://ai\.meta\.com/blog/[^"]+/)"[^>]*>\s*([^<]{10,120})\s*</a>'},
    {"name": "Mistral",         "url": "https://mistral.ai/news",                  "lang": "en", "max_articles": 6,
     "pattern": r'href="(/news/[^"]+)"[^>]*>.*?(?:<h[23][^>]*>([^<]+)</h[23]>|class="[^"]*title[^"]*"[^>]*>([^<]+)<)',
     "dotall": True},

    # ── Chinese: 有博客的厂商 ──
    {"name": "MiniMax",         "url": "https://www.minimaxi.com/blog",            "lang": "zh", "max_articles": 6,
     "pattern": r'href="(/(?:blog|news)/[^"]+)"[^>]*>.*?(?:<h[23][^>]*>([^<]+)</h[23]>|class="[^"]*title[^"]*"[^>]*>([^<]+)<)',
     "dotall": True},
    {"name": "Qwen",            "url": "https://qwenlm.github.io/blog",           "lang": "en", "max_articles": 6,
     "pattern": r'href="(/blog/[^"]+)"[^>]*>\s*([^<]{10,100})\s*</a>'},

    # ── Chinese: 文档侧边栏新闻 ──
    {"name": "小米MiMo",        "url": "https://platform.xiaomimimo.com/docs/zh-CN/news/v2.5-orbit", "lang": "zh", "max_articles": 6,
     "pattern": r'href="(/docs/zh-CN/news/[^"]+)"[^>]*>.*?<p[^>]*>([^<]+)</p>',
     "dotall": True},
    {"name": "DeepSeek",        "url": "https://api-docs.deepseek.com/zh-cn/news/news260424", "lang": "zh", "max_articles": 6,
     "pattern": r'href="(/(?:zh-cn/)?news/[^"]+)"[^>]*>\s*([^<]{5,100})\s*</a>'},
    {"name": "智谱AI",           "url": "https://docs.bigmodel.cn/cn/update/new-releases", "lang": "zh", "max_articles": 6,
     "pattern": r'href="#(20\d{2}-\d{2}-\d{2})"[^>]*>\s*[^<]+\s*</a>',
     "single_group": True},
]

# ── Web search keywords (覆盖所有国内厂商) ──
WEB_SEARCH_KEYWORDS = [
    "AI模型 发布 更新 today",
    "DeepSeek 新版本 发布",
    "Kimi Moonshot K2 更新",
    "小米 MiMo 模型 发布",
    "百度文心 ERNIE 更新",
    "腾讯混元 Hunyuan 发布",
    "华为盘古 Pangu 更新",
    "讯飞星火 Spark 发布",
    "百川智能 Baichuan 更新",
    "阶跃星辰 Step 发布",
    "商汤 SenseNova 更新",
    "昆仑天工 SkyWork 发布",
    "MiniMax 智谱GLM 通义千问 更新",
    "36kr 机器之心 量子位 AI模型",
]


def github_api_get(url, token=None):
    """Fetch GitHub API with optional auth token."""
    headers = {
        "User-Agent": "HermesAgent/1.0",
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception:
        return None


def fetch_github_ecosystem():
    """Fetch AI ecosystem data from GitHub API: new skills, MCP servers, rules, etc."""
    token = None
    if os.path.exists(GITHUB_TOKEN_FILE):
        try:
            token = open(GITHUB_TOKEN_FILE).read().strip()
        except Exception:
            pass

    results = []
    now = datetime.now(timezone.utc)
    seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")
    thirty_days_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    # ── 1. Search: new Claude Code skills ──
    q = f"claude code skills created:>{seven_days_ago}"
    data = github_api_get(f"https://api.github.com/search/repositories?q={urlquote(q)}&sort=stars&order=desc&per_page=8", token)
    if data:
        for item in data.get("items", []):
            results.append({
                "title": f"{item['full_name']} ⭐{item['stargazers_count']}",
                "url": item["html_url"],
                "date": item.get("created_at", ""),
                "source": "GitHub/Skills",
                "lang": "en",
                "description": (item.get("description") or "")[:120],
                "stars": item.get("stargazers_count", 0),
            })

    # ── 2. Search: new Cursor rules ──
    q = f"cursor rules created:>{seven_days_ago}"
    data = github_api_get(f"https://api.github.com/search/repositories?q={urlquote(q)}&sort=stars&order=desc&per_page=5", token)
    if data:
        for item in data.get("items", []):
            results.append({
                "title": f"{item['full_name']} ⭐{item['stargazers_count']}",
                "url": item["html_url"],
                "date": item.get("created_at", ""),
                "source": "GitHub/CursorRules",
                "lang": "en",
                "description": (item.get("description") or "")[:120],
                "stars": item.get("stargazers_count", 0),
            })

    # ── 3. Search: AI agent frameworks ──
    q = f"AI agent skills framework created:>{thirty_days_ago}"
    data = github_api_get(f"https://api.github.com/search/repositories?q={urlquote(q)}&sort=stars&order=desc&per_page=5", token)
    if data:
        for item in data.get("items", []):
            results.append({
                "title": f"{item['full_name']} ⭐{item['stargazers_count']}",
                "url": item["html_url"],
                "date": item.get("created_at", ""),
                "source": "GitHub/Agents",
                "lang": "en",
                "description": (item.get("description") or "")[:120],
                "stars": item.get("stargazers_count", 0),
            })

    # ── 4. Search: vibe coding ──
    q = f"vibe coding created:>{thirty_days_ago}"
    data = github_api_get(f"https://api.github.com/search/repositories?q={urlquote(q)}&sort=stars&order=desc&per_page=3", token)
    if data:
        for item in data.get("items", []):
            results.append({
                "title": f"{item['full_name']} ⭐{item['stargazers_count']}",
                "url": item["html_url"],
                "date": item.get("created_at", ""),
                "source": "GitHub/VibeCoding",
                "lang": "en",
                "description": (item.get("description") or "")[:120],
                "stars": item.get("stargazers_count", 0),
            })

    # ── 5. Search: system prompts ──
    q = "system prompts leaks"
    data = github_api_get(f"https://api.github.com/search/repositories?q={urlquote(q)}&sort=stars&order=desc&per_page=5", token)
    if data:
        seen_stars = set()
        for item in data.get("items", []):
            # Skip if already have a repo with similar star count (dedup)
            stars = item.get("stargazers_count", 0)
            if stars in seen_stars:
                continue
            seen_stars.add(stars)
            results.append({
                "title": f"{item['full_name']} ⭐{item['stargazers_count']}",
                "url": item["html_url"],
                "date": item.get("pushed_at", ""),
                "source": "GitHub/Prompts",
                "lang": "en",
                "description": (item.get("description") or "")[:120],
                "stars": item.get("stargazers_count", 0),
            })

    # ── 6. Commits: awesome-mcp-servers new additions ──
    commits = github_api_get(
        f"https://api.github.com/repos/punkpeye/awesome-mcp-servers/commits?per_page=30&since={seven_days_ago}T00:00:00Z",
        token
    )
    if commits:
        for c in commits:
            msg = c.get("commit", {}).get("message", "")
            lower = msg.lower()
            # Look for "add-xxx" pattern in merge commit messages
            add_match = re.search(r"add-([a-z0-9_-]+)", lower)
            if add_match:
                server_name = add_match.group(1)
                first_line = f"New: {server_name}"
                sha = c.get("sha", "")[:8]
                results.append({
                    "title": f"MCP: {first_line}",
                    "url": f"https://github.com/punkpeye/awesome-mcp-servers/commit/{sha}",
                    "date": c.get("commit", {}).get("author", {}).get("date", ""),
                    "source": "GitHub/MCP",
                    "lang": "en",
                    "description": first_line,
                    "stars": 0,
                })

    # ── 7. Commits: antigravity-awesome-skills updates ──
    commits = github_api_get(
        f"https://api.github.com/repos/sickn33/antigravity-awesome-skills/commits?per_page=10&since={seven_days_ago}T00:00:00Z",
        token
    )
    if commits:
        skill_count = 0
        for c in commits:
            msg = c.get("commit", {}).get("message", "")
            if "skill" in msg.lower() or "add" in msg.lower():
                skill_count += 1
        if skill_count > 0:
            results.append({
                "title": f"Antigravity Skills Registry updated ({skill_count} changes this week)",
                "url": "https://github.com/sickn33/antigravity-awesome-skills",
                "date": commits[0].get("commit", {}).get("author", {}).get("date", ""),
                "source": "GitHub/Skills",
                "lang": "en",
                "description": "1494+ agentic skills for Claude Code, Cursor, Codex CLI, Gemini CLI",
                "stars": 39000,
            })

    return results


def fetch_url(url):
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


# ── Hacker News ──
def fetch_hackernews():
    """从 HN Top Stories 中筛选 AI 相关内容"""
    results = []
    try:
        top_ids = json.loads(fetch_url("https://hacker-news.firebaseio.com/v0/topstories.json") or "[]")
    except Exception:
        return results

    # 只检查前 60 条（覆盖首页大部分内容）
    ai_keywords = [
        "ai", "llm", "gpt", "claude", "gemini", "openai", "anthropic", "deepseek",
        "model", "agent", "coding", "cursor", "copilot", "mcp", "rag", "embed",
        "fine-tun", "inference", "transformer", "diffusion", "token",
        "人工智能", "大模型", "智能体", "代码", "编程",
    ]

    for story_id in top_ids[:60]:
        item = github_api_get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
        if not item or item.get("type") != "story":
            continue
        title = item.get("title", "")
        url = item.get("url", "")
        if not title:
            continue
        # 标题匹配 AI 关键词
        title_lower = title.lower()
        if not any(kw in title_lower for kw in ai_keywords):
            continue
        if not url:
            url = f"https://news.ycombinator.com/item?id={story_id}"
        results.append({
            "title": title,
            "url": url,
            "date": datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc).isoformat(),
            "source": "Hacker News",
            "lang": "en",
            "description": f"HN Score: {item.get('score', 0)} | Comments: {item.get('descendants', 0)}",
            "stars": item.get("score", 0),
        })
    return results


# ── GitHub Trending (AI/ML) ──
def fetch_github_trending():
    """搜索近 7 天新建的高星 AI 相关仓库"""
    token = None
    if os.path.exists(GITHUB_TOKEN_FILE):
        try:
            token = open(GITHUB_TOKEN_FILE).read().strip()
        except Exception:
            pass

    results = []
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

    queries = [
        f"AI coding tool created:>{week_ago}",
        f"LLM agent framework created:>{week_ago}",
        f"AI developer tool created:>{week_ago}",
    ]

    seen_ids = set()
    for q in queries:
        data = github_api_get(
            f"https://api.github.com/search/repositories?q={urlquote(q)}&sort=stars&order=desc&per_page=10",
            token
        )
        if not data:
            continue
        for item in data.get("items", []):
            repo_id = item["id"]
            if repo_id in seen_ids:
                continue
            seen_ids.add(repo_id)
            stars = item.get("stargazers_count", 0)
            if stars < 10:  # 过滤太冷门的
                continue
            results.append({
                "title": f"🔥 {item['full_name']} ⭐{stars}",
                "url": item["html_url"],
                "date": item.get("created_at", ""),
                "source": "GitHub/Trending",
                "lang": "en",
                "description": (item.get("description") or "")[:120],
                "stars": stars,
            })

    # 按星数排序，取 top 10
    results.sort(key=lambda x: x.get("stars", 0), reverse=True)
    return results[:10]


def parse_date(date_str):
    if not date_str:
        return None
    formats = [
        "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S",
        "%Y-%m-%d",
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


def is_recent(dt, hours=168):
    if dt is None:
        return True
    dt = make_aware(dt)
    now = datetime.now(timezone.utc)
    diff = now - dt
    return diff.total_seconds() < hours * 3600


def is_relevant(title):
    title_lower = title.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw.lower() in title_lower:
            return False
    for kw in INCLUDE_KEYWORDS:
        if kw.lower() in title_lower:
            return True
    return False


def load_tracking():
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
    except (json.JSONDecodeError, OSError):
        pass
    return set(), None


def save_tracking(urls, last_run_time):
    os.makedirs(os.path.dirname(TRACKING_FILE), exist_ok=True)
    with open(TRACKING_FILE, "w") as f:
        json.dump({
            "urls": sorted(list(urls))[-500:],
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


def parse_html_blog(content, source_name, source_lang, pattern, base_url, single_group=False, dotall=False):
    articles = []
    if not content:
        return articles

    flags = re.IGNORECASE
    if dotall:
        flags |= re.DOTALL

    matches = re.findall(pattern, content, flags)
    seen_urls = set()

    for match in matches:
        if single_group:
            path = match
            title = match
        elif isinstance(match, tuple):
            path = match[0]
            title = next((m for m in match[1:] if m), match[0])
        else:
            path = match
            title = match

        title = title.strip()
        if not title or len(title) < 5:
            continue

        # Skip generic labels
        if title.lower() in ["往期新闻", "news", "previous news"]:
            continue

        if path.startswith("http"):
            url = path
        elif path.startswith("/"):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            url = f"{parsed.scheme}://{parsed.netloc}{path}"
        else:
            url = f"{base_url.rstrip('/')}/{path}"

        if url in seen_urls:
            continue
        seen_urls.add(url)

        if any(x in title.lower() for x in ["skip to", "api key", "sign up", "log in"]):
            continue

        # Skip generic labels AFTER adding to seen_urls to avoid blocking real articles with same URL
        if title.lower() in ["english", "中文", "中文（中国）", "往期新闻", "news", "previous news"]:
            seen_urls.discard(url)  # Remove so real article with same URL can pass
            continue

        articles.append({
            "title": title,
            "url": url,
            "date": None,
            "source": source_name,
            "lang": source_lang
        })

    return articles


def main():
    seen, last_run = load_tracking()
    now = datetime.now(BEIJING_TZ)

    if last_run is None:
        last_run = now.replace(hour=0, minute=0, second=0, microsecond=0)

    session_urls = set()
    all_articles = []
    errors = []
    stats = {"rss": 0, "html": 0, "filtered": 0}

    # ── RSS ──
    for feed in RSS_FEEDS:
        content = fetch_url(feed["url"])
        if content is None:
            errors.append(feed["name"])
            continue
        fmt = feed.get("format", "xml")
        if fmt == "json":
            articles = parse_json_feed(content, feed["name"], feed.get("lang", "en"))
        else:
            articles = parse_feed(content, feed["name"], feed.get("lang", "en"))

        max_articles = feed.get("max_articles", 6)
        count = 0
        for art in articles:
            if count >= max_articles:
                break
            if art["url"] in seen or art["url"] in session_urls:
                continue
            if not is_recent(art["date"], hours=72):
                continue
            if not is_relevant(art["title"]):
                stats["filtered"] += 1
                continue  # 不加入 session_urls，允许同 URL 不同标题的文章通过
            all_articles.append(art)
            session_urls.add(art["url"])
            count += 1
        stats["rss"] += count

    # ── HTML blogs/docs ──
    for blog in HTML_BLOGS:
        content = fetch_url(blog["url"])
        if content is None:
            errors.append(blog["name"])
            continue
        articles = parse_html_blog(
            content,
            blog["name"],
            blog.get("lang", "en"),
            blog["pattern"],
            blog["url"],
            blog.get("single_group", False),
            blog.get("dotall", False)
        )

        max_articles = blog.get("max_articles", 6)
        count = 0
        for art in articles:
            if count >= max_articles:
                break
            if art["url"] in seen or art["url"] in session_urls:
                continue
            if not is_relevant(art["title"]):
                stats["filtered"] += 1
                continue  # 不加入 session_urls，允许同 URL 不同标题的文章通过
            all_articles.append(art)
            session_urls.add(art["url"])
            count += 1
        stats["html"] += count

    save_tracking(seen | session_urls, now)

    # ── Hacker News (AI 相关) ──
    hn_articles = fetch_hackernews()
    hn_new = []
    for art in hn_articles:
        if art["url"] not in seen and art["url"] not in session_urls:
            hn_new.append(art)
            session_urls.add(art["url"])

    # ── GitHub Trending (AI/ML 新工具) ──
    trending_articles = fetch_github_trending()
    trending_new = []
    for art in trending_articles:
        if art["url"] not in seen and art["url"] not in session_urls:
            trending_new.append(art)
            session_urls.add(art["url"])

    # ── GitHub ecosystem data ──
    github_articles = fetch_github_ecosystem()
    # Deduplicate against existing URLs
    github_new = []
    for art in github_articles:
        if art["url"] not in seen and art["url"] not in session_urls:
            github_new.append(art)
            session_urls.add(art["url"])

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
        "github_count": len(github_new),
        "hackernews_count": len(hn_new),
        "trending_count": len(trending_new),
        "stats": stats,
        "articles": serializable,
        "github_ecosystem": github_new,
        "hackernews": hn_new,
        "github_trending": trending_new,
        "errors": errors,
        "web_search_keywords": WEB_SEARCH_KEYWORDS,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
