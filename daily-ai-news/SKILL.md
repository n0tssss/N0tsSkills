---
name: daily-ai-news
description: |
  AI news briefing v4 — fetches from 18+ sources (6 RSS + 8 HTML + HN + GitHub Trending + GitHub Ecosystem),
  keyword filtering for model releases & developer tools, web-searches Chinese AI news, delivers curated digest.
trigger: Cron job with LLM mode + web search
---

# Daily AI News v4

Delivers a **curated, filtered** AI briefing focused on what matters:
- Model releases & updates
- API/SDK changes
- Developer tools & coding agents
- Open source releases
- Community trends & hot discussions

## Architecture

```
RSS (6) + HTML (8) + Hacker News + GitHub Trending + GitHub Ecosystem
        │
        ▼
  ai-news.py (fetch + filter + dedup)
        │
        ▼
  JSON output → LLM cron prompt (summarize + web_search 补充)
        │
        ▼
  Curated digest (~50 items)
```

## Design principle: script extracts, LLM reasons

**脚本只负责机械工作**：HTTP 请求、HTML 解析、URL 去重、时间过滤。
**脚本不做任何内容过滤**：不判断相关性、不排除噪音、不分类。

LLM 负责所有语义工作：翻译、归类、过滤噪音、按重要性排序。

原因：关键词匹配无法理解上下文（如"Singular Bank 用 ChatGPT"是案例不是新闻），LLM 可以判断"这个发布对用户有没有用"。

### 用户内容优先级（LLM 排序依据）
1. **新模型发布** — 什么模型发布了？有什么新能力？
2. **重磅新闻** — 行业大事件、重大更新
3. **实用工具** — 能让开发者实际用上的东西（API、SDK、开源项目）
4. **技术突破** — 论文、benchmark、新方法

### Output Format
- Output **news summary**, not statistics
-按重要性分组，不按来源分组
- 最新的模型发布必须排在最前面

### New Output Section: AI 新姿势

在现有板块之后增加 `🚀 AI 新姿势` 板块，内容来源为 GitHub API 数据：

```
🚀 AI 新姿势
（本周新发现的 Skills、Plugins、工具、工作流）
- [项目名](link) ⭐N — 一句话说明这个东西能干嘛
```

按以下子类别组织（不是每个都有内容时才输出）：
- **Skills & Plugins** — Claude Code / Cursor / Hermes 新技能包
- **MCP 新发现** — 本周新增的 MCP server
- **规则与配置** — Cursor Rules / System Prompt / AGENTS.md
- **新范式** — Vibe Coding / 新的 AI 使用方式

## How it works

1. **Script** `scripts/ai-news.py` fetches RSS/HTML sources + GitHub API data, deduplicates, outputs raw articles
2. **LLM cron job** reads the raw JSON, filters by relevance, summarizes, uses `web_search` for additional Chinese AI news
3. **Delivery** — cron output goes directly to configured chat

## Data Sources Architecture

```
RSS feeds (6 sources)             HTML/doc blogs (9 sources)        GitHub API (6 queries)
        │                                    │                              │
        ▼                                    ▼                              ▼
  ai-news.py (fetch + keyword filter + dedup + GitHub API)         LLM cron prompt (summarize + search)
        │                                    │                              │
        └─────────────┬──────────────────┘                              │
                         └──────────────────────────────────────────────────┘
                                        ▼
                              Curated digest (~50 articles)
```

### GitHub API Sources (for "AI 新姿势" category)

GitHub API with auth token provides **structured, high-quality data** on AI ecosystem trends. This is far superior to web_search for tracking new tools, skills, and plugins.

**Why GitHub API over web_search:**
- web_search returns water content, blogspam, SEO articles
- GitHub API returns actual projects with star counts, descriptions, creation dates
- Can track new repos by `created:>YYYY-MM-DD` filter
- Can track commits to awesome-* lists to detect new additions

**Queries to run (in ai-news.py):**

**6 search queries + 2 commit tracking (in `fetch_github_ecosystem()`):**

| Query | Source Label | Per Page | Purpose |
|-------|-------------|----------|---------|
| `claude code skills created:>7d` | GitHub/Skills | 8 | New Claude Code skill repos |
| `cursor rules created:>7d` | GitHub/CursorRules | 5 | New Cursor/Windsurf rules |
| `AI agent skills framework created:>30d` | GitHub/Agents | 5 | New agent frameworks |
| `vibe coding created:>30d` | GitHub/VibeCoding | 3 | Vibe coding paradigm |
| `system prompts leaks` | GitHub/Prompts | 5 | System prompt collections (no date filter) |
| awesome-mcp-servers commits (7d) | GitHub/MCP | 30 commits | New MCP server additions via "add-xxx" pattern |
| antigravity-awesome-skills commits (7d) | GitHub/Skills | 10 commits | Skills registry updates |

**Key repos to track (commit-based):**
- `punkpeye/awesome-mcp-servers` — merge commits with "add-xxx" pattern = new MCP servers
- `sickn33/antigravity-awesome-skills` — 1494+ skills registry, commit messages indicate skill changes

**Rate limiting:** GitHub API requires auth token for 5000 req/hour. Unauthenticated: 60/hour. Token stored at `~/.hermes/.github_token`.

**Implementation:** `fetch_github_ecosystem()` function in `ai-news.py` handles all GitHub API calls. Returns list of dicts with same structure as RSS articles plus `description` and `stars` fields. Output JSON has `github_ecosystem` array alongside `articles`.

## Key Features

### Smart Filtering
- **Include keywords**: model names (GPT, Claude, Gemini, DeepSeek, Qwen, GLM, MiniMax, MiMo...), release/update terms, API/SDK, open source, benchmarks
- **Exclude keywords**: hiring, jobs, opinions, partnerships, enterprise/commercial, politics
- **Time window**: RSS articles from last 72 hours only
- **Per-source limits**: Max 8-10 articles per source
- **Target**: ~50 articles total (down from 1200+ unfiltered)

### Sources (14 total)

**RSS Feeds (6)**
| Source | Max | Focus |
|--------|-----|-------|
| OpenAI Blog | 10 | GPT releases, API updates |
| Google AI Blog | 10 | Gemini, PaLM updates |
| The Verge AI | 8 | Industry news |
| TechCrunch AI | 8 | Startup/product launches |
| VentureBeat AI | 8 | Enterprise AI |
| Hugging Face Papers | 8 | Daily papers |

**HTML Blogs (9)**
| Source | URL | Type | Focus |
|--------|-----|------|-------|
| Anthropic | anthropic.com/news | blog | Claude releases |
| Meta AI | ai.meta.com/blog | blog | Llama releases |
| Mistral | mistral.ai/news | blog | Mistral releases |
| MiniMax | minimaxi.com/blog | blog | MiniMax updates |
| Qwen | qwenlm.github.io/blog | blog | Qwen releases |
| 智谱AI | docs.bigmodel.cn/.../new-releases | doc | GLM updates |
| DeepSeek | api-docs.deepseek.com/zh-cn/news/... | doc | DeepSeek releases |
| 小米MiMo | platform.xiaomimimo.com/docs/zh-CN/news/... | doc | MiMo updates |

**Web Search (supplementary — vendors without public blogs)**
- Kimi/Moonshot, 百度文心 ERNIE, 腾讯混元, 华为盘古
- 讯飞星火, 百川智能, 阶跃星辰, 商汤日日新, 昆仑天工
- Keywords: `AI模型 发布 更新 today`, `DeepSeek Kimi 豆包 新版本`, `36kr 机器之心 量子位`

## LLM Prompt

```
你是一个 AI 科技资讯编辑。以下是经过筛选的 AI 新闻数据（30-60篇），都是与模型更新、API变更、工具发布相关的干货。

用户最关心的内容优先级：
1. **新模型发布** — 什么模型发布了？有什么新能力？
2. **重磅新闻** — 行业大事件、重大更新
3. **实用工具** — 能让开发者实际用上的东西（API、SDK、开源项目）
4. **AI 新姿势** — Skills、Plugins、MCP server、Cursor Rules、新工作流（来源：GitHub API）
5. **技术突破** — 论文、benchmark、新方法

你的任务：

1. **整理摘要** — 按以下格式输出，重点突出最新发布：

```
🤖 AI 资讯速递 | {fetch_time}
（上次更新：{last_run}）

🔥 重点发布
（选出3-5条最重要的发布，按时间倒序，最新的在最前面）
（每条：模型名称 + 一句话说清楚发布了什么 + 链接）

📡 模型更新
（其他模型更新，同样按时间倒序）

🚀 AI 新姿势
（本周新发现的 Skills、Plugins、MCP、Rules、工作流）
（来源：GitHub API 数据，包含 star 数和项目描述）
（每条：项目名 + star 数 + 一句话说清楚能干嘛 + 链接）

🛠️ 工具与平台
（开发者工具、API变更、开源项目）

🇨🇳 国内动态
（国内厂商新闻）

📄 论文精选
（最有价值的2-3篇论文）

---
🤖 by Hermes Agent | {count} articles + GitHub ecosystem data
```

2. **搜索补充** — 使用 web_search 搜索：
   - "AI模型 发布 更新 today"
   - "DeepSeek Kimi 豆包 新版本"
   - 关注：36kr、机器之心、量子位

3. **注意事项**：
   - 每条新闻必须有完整可点击 URL
   - **按发布时间倒序**，最新的模型发布必须排在最前面
   - 一句话点评突出**用户能用上什么**，不要堆砌形容词
   - 如果某类别没有新闻，省略该类别
   - 不要按来源分组，要按**重要性**分组
   - "AI 新姿势"板块的数据来自 GitHub API，按 star 数排序，优先推荐 star 高的项目
```

## Filtering Keywords

### Include
```
release, launch, announce, introducing, new model, update
发布, 上线, 更新, 升级, 推出, 新增
gpt, o3, o4, claude, gemini, llama, mistral, grok
deepseek, qwen, glm, baichuan, yi, minimax, step, mimo
doubao, kimi, hunyuan, pangu, spark, ernie, moonshot
api, sdk, tool, platform, developer, pricing, cursor, copilot
open source, open-source, github, huggingface, 开源
benchmark, performance, context window, reasoning, coding
基准, 性能, 上下文, 推理, 编程
```

### Exclude
```
hiring, job, career, office, expansion
招聘, 职位, 办公, 扩张
podcast, interview, opinion, editorial
播客, 访谈, 观点
sponsor, partner, collaboration
赞助, 合作
enterprise, 企业级, 商业化, 落地, 生态
president, minister, government
总统, 部长, 政府
```

## Cron Job Setup

```bash
hermes cron create \
  --script ai-news.py \
  --schedule "0 8,13 * * *" \
  --name "daily-ai-news" \
  --prompt "..." \
  --enabled-toolsets "terminal,web,file"
```

## Pitfalls

### HTML blogs don't have dates
HTML blog articles don't have publish dates, so we take the first N (assuming newest first) and filter by keywords only.

### Some sites need DOTALL regex
Anthropic, Mistral, MiniMax put titles in h2/h3 tags after the href, not inline. Pattern needs `re.DOTALL` to match across newlines: `href="(/news/[^"]+)"[^>]*>.*?<h[23][^>]*>([^<]+)</h[23]>`.

### DeepSeek news URL is nested
DeepSeek's news list is at `api-docs.deepseek.com/news/news260424` (a specific article page that also lists older news), NOT at `/news`.

### Most Chinese AI vendors have no public blog
Kimi, 百度文心, 腾讯混元, 华为盘古, 讯飞星火, 百川, 阶跃, 商汤, 昆仑 — none have scrapable blog/news pages. Must use `web_search` in the LLM prompt.

### Doc sidebar scraping (MiMo, DeepSeek pattern)
Some vendors hide news in their API documentation sidebars instead of public blogs. Pattern to scrape:
1. Fetch any doc page (e.g., `platform.xiaomimimo.com/docs/zh-CN/news/v2.5-orbit`)
2. Extract news URLs from sidebar: look for `data-doc-nav-href` or `href` with `/news/` or `/docs/.../news/` paths
3. Pair with title text: `href="(/docs/.../news/[^"]+)"[^>]*>.*?<p[^>]*>([^<]+)</p>` (MiMo style)
4. Or: `href="(/(?:zh-cn/)?news/[^"]+)"[^>]*>\s*([^<]{5,100})\s*</a>` (DeepSeek style)
5. Must use `re.DOTALL` flag since content spans multiple lines in sidebar HTML

### `seen_urls` dedup bug with navigation labels
**Critical pitfall**: When parsing HTML, if navigation labels (e.g., "English", "中文") are excluded AFTER adding URL to `seen_urls`, it blocks legitimate articles sharing the same URL. Example: DeepSeek sidebar has `English -> /news/news260424` and `DeepSeek-V4 -> /zh-cn/news/news260424` — same URL, different titles. If "English" is excluded but its URL stays in `seen_urls`, V4 gets deduped out.

**Fix**: Check navigation keywords BEFORE adding to `seen_urls`, OR use `seen_urls.discard(url)` when skipping nav labels so the real article can pass.

### OpenAI RSS returns all history
OpenAI's RSS feed returns 900+ articles. We limit to 10 and filter by time (72h) + keywords.

### User preference: model updates > commercial news
User explicitly wants model release/update news, NOT commercial partnerships, enterprise deals, or expansion announcements. Keep exclude keywords tight on business/political content.

### Don't miss important releases when organizing
When organizing articles by importance, scan ALL articles first before writing the summary. Don't just pick from the top of the list. Important releases like MiniMax M3 can be buried in the middle of a source's article list.

### Output is a news summary, not statistics
User explicitly said: "我要看的是新闻而不是你的统计". Never output counts, source breakdowns, or filtering stats. Just give the news, organized by importance.

### Subagent delegation unreliable for web_search
On mimo-v2.5, delegate_task subagents may return empty/short results when doing web_search. If web_search is needed in the cron job, do it directly in the LLM prompt rather than delegating. GitHub API calls via terminal are reliable.

### skill_manage can't find skills with category prefix
`skill_manage(action='patch', name='N0tsSkills/daily-ai-news')` fails with "not found in active profile". The tool only recognizes bare skill names. Use `patch()` tool directly on the SKILL.md file path instead, or use `skill_manage` without the category prefix.

### GitHub API requires auth for volume
Unauthenticated GitHub API: 60 requests/hour. With token: 5000/hour. The ai-news.py script must read `~/.hermes/.github_token` for all GitHub API calls.

## Tracking

- Seen URLs: last 500 stored in `~/.hermes/data/ai-news-seen.json`
- `last_run` timestamp for incremental fetching
- Falls back to start-of-today if no `last_run`

## References

- `references/vendor-websites.md` — Chinese AI vendor website research (which have blogs, which need web_search)
- `references/vendor-docs-scraping.md` — Doc sidebar scraping patterns (MiMo, DeepSeek)
- `references/github-api-ecosystem-sources.md` — GitHub API queries and tracking repos for AI ecosystem news
- `references/github-api-ecosystem.md` — GitHub API ecosystem tracking patterns, MCP commit parsing, auth token usage, and pitfalls
