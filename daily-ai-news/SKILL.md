---
name: daily-ai-news
description: |
  AI news briefing — fetches from 14 RSS/JSON sources, LLM filters for tech substance
  (GPT/Gemini/Claude/models/tools), web-searches Chinese AI news, and delivers a categorized
  summary with links to WeChat twice daily at 8:00 and 13:00.
trigger: Cron job runs twice daily at 08:00 and 13:00 with LLM mode + web search
---

# Daily AI News

Delivers a curated AI briefing to WeChat twice daily (08:00 and 13:00 Beijing time).
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
          Categorized WeChat digest
```

## How it works

1. **Script** `scripts/ai-news.py` fetches 14 RSS/JSON feeds, deduplicates by URL, filters to articles **since the last run** (incremental fetching via `last_run` timestamp in tracking file), outputs JSON to stdout
2. **LLM cron job** reads the JSON, filters for substantive AI tech news (GPT/Gemini/Claude/models/tools/research), uses `web_search` to find Chinese AI news (DeepSeek, 通义, 文心, 豆包, Kimi, GLM, etc.), and writes a categorized summary
3. **Delivery** — cron output goes directly to the user's WeChat chat

## Filtering criteria (LLM prompt)

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

## Output format

```
🤖 AI 资讯速递 | YYYY年MM月DD日 HH:MM
（上次更新：YYYY-MM-DD HH:MM）

🔥 重点新闻
（最重要新闻 + 点评）

📡 模型资讯
- [title](link) — one-line take

🛠️ 工具与开源
- [title](link) — one-line take

🇨🇳 国内动态
- [title](link) — one-line take

📄 论文
- [title](link) — one-line take
---
🤖 by Hermes Agent | 14 RSS sources + Web search
```

## Cron job setup

```bash
hermes cron create \
  --script ai-news.py \
  --schedule "0 8,13 * * *" \
  --name "daily-ai-news" \
  --prompt "..." \
  --enabled-toolsets "terminal,web,file"
```

Schedule: twice daily at 08:00 and 13:00 Beijing time.
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
