---
name: daily-weather
description: "每日天气卡片 — 采集数据 → AI翻译 → 渲染图片。不同天气自动切换背景。"
version: 2.0.0
author: N0ts
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [weather, forecast, daily, image]
---

# 每日天气卡片

## 流程

```
fetch_weather_data.py → 原始JSON(英文) → AI翻译 → 写入翻译JSON → render_weather.py --data-file → 图片
```

**为什么需要 AI 翻译？** wttr.in 的 `lang=zh` 参数不返回中文描述，脚本自带的字典覆盖不全。AI 翻译准确率 100%。

## 首次使用

首次收到天气请求时，用 `clarify` 问用户：
> 你想查哪个城市的天气？（如：北京、上海、深圳）

获得城市后，存入 memory：
```
memory(action="add", target="user", content="天气查询默认城市：XXX")
```

## 执行步骤（Agent 模式）

### Step 1: 采集数据
```bash
python3 ~/.hermes/skills/daily-weather/scripts/fetch_weather_data.py --city "城市名" --mode today
```

输出 JSON，关键字段：
- `weather_en` — 英文天气描述（需翻译）
- `hourly[].weather_en` — 每个时段的英文描述（需翻译）

### Step 2: AI 翻译
把所有 `weather_en` 翻译成自然中文，如：
- "Patchy rain nearby" → "附近有零星小雨"
- "Partly cloudy" → "多云"
- "Light rain shower" → "小阵雨"

给每个时段加上 `emoji` 字段（根据翻译后的天气描述选择合适 emoji）。

判断当前时段（`is_now: true`）。

### Step 3: 写入 JSON 并渲染
将翻译后的数据写入临时文件，然后：
```bash
python3 ~/.hermes/skills/daily-weather/scripts/render_weather.py --data-file /tmp/weather_translated.json
```

### Step 4: 发送图片
```
MEDIA:/Users/wkea/.hermes/cache/weather_card.png
```

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
- 逐8时段预报
- 💡 生活建议（穿衣/带伞/防风等）
- 风力风向 + 湿度
- 日出日落
- 节假日/周末倒计时

## 注意事项
- `--city` 必填，无默认城市
- 节假日数据每年需更新 `LUNAR_HOLIDAYS_YYYY`
- 渲染需要 Playwright + Chromium
