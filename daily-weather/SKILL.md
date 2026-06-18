---
name: daily-weather
description: "每日天气卡片 — 查询天气并渲染为精美图片，不同天气自动切换背景。首次使用需输入城市。"
version: 1.0.0
author: N0ts
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [weather, forecast, daily, image]
---

# 每日天气卡片

## 功能
- 查询全球城市天气（wttr.in API）
- 渲染为精美图片卡片，不同天气自动切换背景
- 支持今日/明日天气、节假日倒计时、生活建议

## ⚠️ 首次使用（重要）

**脚本没有默认城市，必须传入 `--city` 参数。**

首次收到天气相关请求时，用 `clarify` 工具问用户：
> 你想查哪个城市的天气？（如：北京、上海、深圳）

获得城市后，存入 memory：
```
memory(action="add", target="user", content="天气查询默认城市：XXX")
```

后续请求直接从 memory 读取城市，不再追问。

## 用法

### 图片输出（推荐）
```bash
python3 ~/.hermes/skills/daily-weather/scripts/render_weather.py --city "北京" --mode today
python3 ~/.hermes/skills/daily-weather/scripts/render_weather.py --city "上海" --mode tomorrow
```

### 文本输出（备用）
```bash
python3 ~/.hermes/skills/daily-weather/scripts/weather.py --city "北京" --mode today
```

### 参数
- `--city` **（必填）**：城市名，支持中文和英文
- `--mode`：`today`（今天）或 `tomorrow`（明天，默认）
- `--output`：图片输出路径（默认 `~/.hermes/cache/weather_card.png`）

## 图片背景自动切换

| 天气 | 背景 |
|------|------|
| ☀️ 晴天 | 蓝天渐变 |
| 🌙 夜晚 | 深蓝夜空 |
| ⛅ 多云 | 紫色渐变 |
| ☁️ 阴天 | 灰白渐变 |
| 🌧️ 雨天 | 深蓝灰 |
| ⛈️ 雷暴 | 深紫黑 |
| ❄️ 雪天 | 浅灰白 |
| 🌫️ 雾霾 | 灰色渐变 |

## 输出内容
- 城市名 + 天气 emoji
- 日期 + 星期
- 主天气 + 温度范围 + 心情 emoji
- 逐8时段预报（00/03/06/09/12/15/18/21点）
- 💡 生活建议（穿衣/带伞/防风等）
- 风力风向 + 湿度
- 日出日落
- 节假日/周末倒计时

## 技术栈
- 数据源：wttr.in（免费，无需 API key）
- 渲染：Playwright + Chromium 截图（390px 宽，2x Retina）
- 模板：`templates/weather_card.html`

## 注意事项
- 中文城市名需 URL 编码（脚本已内置处理）
- 节假日数据每年需更新 `LUNAR_HOLIDAYS_YYYY` 变量
- 农历节日日期每年变化，公历节日一般不用改
