---
name: daily-ai-news
description: |
  AI news briefing — fetches from 14 RSS/JSON sources, LLM filters for tech substance
  (GPT/Gemini/Claude/models/tools), web-searches Chinese AI news, and delivers a categorized
  summary with links.
trigger: Cron job with LLM mode + web search
---

# Daily AI News

Delivers a curated AI briefing.
Combines RSS aggregation + LLM filtering + web search for Chinese sources.
Each run fetches only articles since the last run (incremental), avoiding duplicates.

## Architecture

```
RSS feeds (14 sources)           Web search (Chinese AI)
        │                                │
        ▼                                ▼
  ai-news.py (fetch + dedup)    LLM cron prompt (filter + search + summarize)
        │                                │
        └─────────────┬──────────────────┘
                      ▼
          Categorized digest
```

## How it works

1. **Script** `scripts/ai-news.py` fetches 14 RSS/JSON feeds, deduplicates by URL, filters to articles **since the last run** (incremental fetching via `last_run` timestamp in tracking file), outputs JSON to stdout
2. **LLM cron job** reads the JSON, filters for substantive AI tech news, uses `web_search` to find Chinese AI news, and writes a categorized summary
3. **Delivery** — cron output goes directly to the configured chat

## LLM Prompt

```
你是一个 AI 科技资讯编辑。以下是最新的新闻数据（JSON 格式），来自多个 RSS 源，包含从上次更新到现在的增量新闻。

你的任务：

1. **筛选** — 严格保留真正有价值的 AI 技术资讯，包括：
   - 模型发布/更新（GPT、Gemini、Claude、Llama、DeepSeek、Qwen、GLM 等）
   - AI 工具与基础设施（Cursor、Copilot、LangChain、vLLM、Ollama 等）
   - 重大 AI 研究突破
   - 中国 AI 生态新闻
   - AI 开发者平台/API 变更

2. **搜索补充** — 使用 web_search 搜索今天的中文 AI 新闻：
   - 搜索关键词："AI 新闻 today"、"大模型 发布"、"人工智能 最新"
   - 关注：DeepSeek、通义千问、文心一言、豆包、Kimi、GLM、智谱等中国 AI 公司
   - 搜索中国科技媒体：36kr、机器之心、量子位、AI科技评论等
   - **重要：web_search 结果必须提取完整文章 URL（如 https://36kr.com/p/123456），不能只写主域名（如 https://36kr.com/）**

3. **分类整理** — 按以下格式输出：

```
🤖 AI 资讯速递 | {fetch_time}
（上次更新：{last_run}）

🔥 重点新闻
（选出1-2条最重要新闻，附简短点评）

📡 模型资讯
- [title](完整URL) — 一句话点评

🛠️ 工具与开源
- [title](完整URL) — 一句话点评

🇨🇳 国内动态
- [title](完整URL) — 一句话点评

📄 论文
- [title](完整URL) — 一句话点评

---
🤖 by Hermes Agent | {count} articles from RSS + Web search
```

4. **注意事项**：
   - **每条新闻必须有完整可点击的 URL，不能是主域名**
   - 中英文新闻混合呈现
   - 每条新闻一句话点评，突出技术价值
   - 如果某类别没有新闻，省略该类别
   - 标题使用中文，链接文字保留原文
```

## Filtering criteria

**Include:**
- Model releases / updates (GPT, Gemini, Claude, Llama, DeepSeek, Qwen, GLM, etc.)
- AI tools & infrastructure (Cursor, Copilot, LangChain, vLLM, Ollama, etc.)
- Significant AI research breakthroughs
- Chinese AI ecosystem news
- AI developer platform / API changes

**Exclude:**
- AI music/art/culture commentary
- Pure opinion pieces
- General-interest social commentary about AI
- Articles only about AI investing/business without tech substance

## Cron job setup

```bash
hermes cron create \
  --script ai-news.py \
  --schedule "0 8,13 * * *" \
  --name "daily-ai-news" \
  --prompt "..." \
  --enabled-toolsets "terminal,web,file"
```

Schedule: configurable via cron schedule parameter.
Script runs first → stdout injected as context → LLM processes with web search.
Not `--no-agent` — LLM needed for filtering, summarizing, and web search.

## Sources (14 feeds)

| Source | Format | Language |
|--------|--------|----------|
| OpenAI Blog | RSS | en |
| Google AI Blog | RSS | en |
| The Verge AI | Atom | en |
| The Decoder | RSS | en |
| TechCrunch AI | RSS | en |
| VentureBeat AI | RSS | en |
| Ars Technica AI | RSS | en |
| MIT Tech Review AI | RSS | en |
| Hugging Face Papers | JSON API | en |
| arXiv cs.AI | RSS | en |
| arXiv cs.CL | RSS | en |
| Last Week in AI | RSS | en |
| Synced Review | RSS | en |
| Analytics India Mag | RSS | en |

## Tracking

Seen URLs and `last_run` timestamp stored at `~/.hermes/data/ai-news-seen.json`.
The `last_run` field is updated each run to enable incremental fetching — only articles published after the last run are included. Falls back to start-of-today if no `last_run` exists.

## Script reference

- `scripts/ai-news.py` — Python RSS/JSON aggregator, outputs deduplicated JSON
