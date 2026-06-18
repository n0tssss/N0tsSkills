# Model Vendor Doc Scraping Patterns

How to extract news from AI model vendor documentation pages.

## Pattern: Doc Sidebar News

Some vendors put their changelog/news in the doc site sidebar. By fetching any doc page,
you can extract all news entries from the sidebar navigation.

### DeepSeek
- **URL**: `https://api-docs.deepseek.com/zh-cn/news/news260424` (latest news page)
- **Pattern**: `href="(/(?:zh-cn/)?news/[^"]+)"[^>]*>\s*([^<]{5,100})\s*</a>`
- **Note**: Sidebar lists all news items. Title format: "DeepSeek-V4 预览版发布 2026/04/24"
- **Pitfall**: Same URL appears multiple times (English label, 中文 label, actual article). English/中文 labels must be excluded without adding URL to seen_urls, or the real article with same URL gets deduplicated.

### 小米 MiMo
- **URL**: `https://platform.xiaomimimo.com/docs/zh-CN/news/v2.5-orbit` (any news page)
- **Pattern**: `href="(/docs/zh-CN/news/[^"]+)"[^>]*>.*?<p[^>]*>([^<]+)</p>` (DOTALL)
- **Note**: Sidebar uses `data-doc-nav-href` attribute. Titles in `<p>` tags.
- **Pitfall**: "previous-news" is a category page, skip it.

### 智谱 AI
- **URL**: `https://docs.bigmodel.cn/cn/update/new-releases`
- **Pattern**: `href="#(20\d{2}-\d{2}-\d{2})"[^>]*>\s*[^<]+\s*</a>` (single_group=True)
- **Note**: Date-anchored sections, not traditional links.

## Pattern: Blog Pages

### MiniMax
- **URL**: `https://www.minimaxi.com/blog`
- **Pattern**: `href="(/(?:blog|news)/[^"]+)"[^>]*>.*?(?:<h[23][^>]*>([^<]+)</h[23]>)` (DOTALL)
- **Note**: Titles in h2/h3 tags after the href.

### Anthropic / Mistral
- **URL**: `anthropic.com/news` / `mistral.ai/news`
- **Pattern**: Same h2/h3 pattern as MiniMax
- **Note**: Most titles are in heading tags, not inline text.

### Meta AI
- **URL**: `https://ai.meta.com/blog/`
- **Pattern**: `href="(https://ai\.meta\.com/blog/[^"]+/)"[^>]*>\s*([^<]{10,120})\s*</a>`
- **Note**: Full URLs in href, inline text for title.

### Qwen
- **URL**: `https://qwenlm.github.io/blog`
- **Pattern**: `href="(/blog/[^"]+)"[^>]*>\s*([^<]{10,100})\s*</a>`

## Vendors WITHOUT Public Blog/News Pages

Must use web_search:
- Kimi/Moonshot, 百度文心, 腾讯混元, 华为盘古
- 讯飞星火, 百川智能, 阶跃星辰, 商汤日日新, 昆仑万维天工

## Key Deduplication Pitfall

When a page has the same URL appearing multiple times (e.g., language selector + actual article),
the nav label exclusion must NOT add the URL to `seen_urls`:

```python
# RIGHT: discard URL when skipping nav labels
if url in seen_urls: continue
seen_urls.add(url)
if title in ["English", "中文", "中文（中国）"]:
    seen_urls.discard(url)  # Allow real article through
    continue
```
