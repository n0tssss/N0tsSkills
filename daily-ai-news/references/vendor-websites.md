# Chinese AI Model Vendor Website Research

Last updated: 2026-06-01

## Vendors with Scrapable News Sources

| Vendor | URL | Type | Pattern | Notes |
|--------|-----|------|---------|-------|
| DeepSeek | api-docs.deepseek.com | Doc sidebar | `href="/zh-cn/news/..." + text` | News list on any news article page |
| 小米MiMo | platform.xiaomimimo.com | Doc sidebar | `href="/docs/.../news/..." + <p>` | Use DOTALL, titles in `<p>` tags |
| 智谱GLM | docs.bigmodel.cn | Update log | `href="#YYYY-MM-DD"` | Date-based anchors, single_group=True |
| MiniMax | minimaxi.com/blog | Blog page | `href="/blog/..." + <h2/h3>` | Standard blog, DOTALL needed |
| Qwen | qwenlm.github.io/blog | Blog page | `href="/blog/..." + text` | GitHub Pages, simple structure |

## Vendors WITHOUT Public Blog/News Pages

These require `web_search` in the LLM prompt:

| Vendor | Model | Official Site | Notes |
|--------|-------|---------------|-------|
| Kimi/Moonshot | K2.6 | kimi.moonshot.cn | Platform page, no news section |
| 百度文心 | ERNIE 4.5 | yiyan.baidu.com | Product page only |
| 腾讯混元 | Hunyuan | hunyuan.tencent.com | Academic-style page |
| 华为盘古 | Pangu | pangu.huawei.com | SSL issues, blocked |
| 讯飞星火 | Spark | xinghuo.xfyun.cn | Open platform, no news |
| 百川智能 | Baichuan | baichuan-ai.com | Product homepage |
| 阶跃星辰 | Step | stepfun.com | Product homepage |
| 商汤日日新 | SenseNova | sensetime.com | Company site |
| 昆仑天工 | SkyWork | tiangong.cn | Has skywork.ai/blog but empty |

## International Vendors with Blogs

| Vendor | URL | RSS? | Pattern |
|--------|-----|------|---------|
| Anthropic | anthropic.com/news | No | DOTALL, h2/h3 after href |
| Meta AI | ai.meta.com/blog | No | Standard href + text |
| Mistral | mistral.ai/news | No | DOTALL, h2/h3 after href |
| OpenAI | openai.com/blog/rss.xml | Yes | RSS feed |
| Google AI | feeds.feedburner.com/blogspot/gJZg | Yes | RSS feed |

## Scraping Tips

### MiMo sidebar pattern
```python
# Fetch any MiMo news page, extract sidebar links
pattern = r'href="(/docs/zh-CN/news/[^"]+)"[^>]*>.*?<p[^>]*>([^<]+)</p>'
# Must use re.DOTALL — content spans multiple lines
```

### DeepSeek sidebar pattern
```python
# Fetch any DeepSeek news article page, extract sidebar
pattern = r'href="(/(?:zh-cn/)?news/[^"]+)"[^>]*>\s*([^<]{5,100})\s*</a>'
# No DOTALL needed — matches are inline
```

### Dedup gotcha
The same URL (e.g., `/zh-cn/news/news260424`) appears multiple times in sidebar:
- Language selector: "English", "中文（中国）" → should be EXCLUDED
- Actual article: "DeepSeek-V4 预览版发布" → should be INCLUDED

If excluded labels add URL to `seen_urls` before check, real article gets blocked.
Solution: `seen_urls.discard(url)` when skipping nav labels.
