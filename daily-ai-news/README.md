# AI 新闻推送 (daily-ai-news)

AI 科技资讯速递，自动筛选有价值的新闻并分类推送。

## 功能

- 14 个 RSS/JSON 源自动聚合
- LLM 智能筛选（模型发布、AI 工具、研究突破等）
- 中文 AI 新闻 web 搜索补充
- 增量获取，避免重复
- 可配置推送频率（建议每天 1-2 次）

## 数据源

| 来源 | 格式 | 语言 |
|------|------|------|
| OpenAI Blog | RSS | 英文 |
| Google AI Blog | RSS | 英文 |
| The Verge AI | Atom | 英文 |
| TechCrunch AI | RSS | 英文 |
| arXiv cs.AI | RSS | 英文 |
| Hugging Face Papers | JSON | 英文 |
| ... 共 14 个源 | | |

## 输出格式

```
🤖 AI 资讯速递 | 2026年05月28日 08:00

🔥 重点新闻
（最重要新闻 + AI 点评）

📡 模型资讯
- [标题](链接) — 一句话点评

🛠️ 工具与开源
- [标题](链接) — 一句话点评

🇨🇳 国内动态
- [标题](链接) — 一句话点评
```

## 依赖

- Python 3.x
- feedparser（RSS 解析）

## 使用

```bash
# 手动执行
python3 ~/.hermes/scripts/ai-news.py

# 创建定时任务（示例：每天 08:00 和 13:00）
hermes cron create \
  --script ai-news.py \
  --schedule "0 8,13 * * *" \
  --name "daily-ai-news" \
  --enabled-toolsets "terminal,web,file"
```

## 配置

- 增量追踪文件：`~/.hermes/data/ai-news-seen.json`
- 最后运行时间自动更新
- 首次运行获取当天所有文章
- 推送时间通过 cron schedule 参数自定义
