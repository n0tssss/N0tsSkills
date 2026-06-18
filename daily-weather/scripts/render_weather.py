#!/usr/bin/env python3
"""
天气卡片渲染脚本 — 将天气数据渲染为精美图片
用法:
  python3 render_weather.py --city "北京" --mode tomorrow
  python3 render_weather.py --city "上海" --mode today
"""
import json
import sys
import os
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

BJ_TZ = timezone(timedelta(hours=8))

# 天气类型映射到 CSS class
WEATHER_CLASS_MAP = {
    "sunny": ["sunny"],
    "clear": ["clear"],
    "partly cloudy": ["partly_cloudy"],
    "cloudy": ["cloudy"],
    "overcast": ["cloudy"],
    "mist": ["fog"],
    "fog": ["fog"],
    "light rain": ["rainy"],
    "patchy rain nearby": ["rainy"],
    "moderate rain": ["rainy"],
    "heavy rain": ["heavy_rain"],
    "thunderstorm": ["thunderstorm"],
    "light snow": ["snow"],
    "snow": ["snow"],
    "blizzard": ["snow"],
    "drizzle": ["rainy"],
    "showers": ["rainy"],
    "light drizzle": ["rainy"],
}

WEATHER_EMOJI = {
    "sunny": "☀️", "clear": "🌙", "partly cloudy": "⛅",
    "cloudy": "☁️", "overcast": "☁️", "mist": "🌫️",
    "fog": "🌫️", "light rain": "🌦️", "patchy rain nearby": "🌦️",
    "moderate rain": "🌧️", "heavy rain": "🌧️", "thunderstorm": "⛈️",
    "light snow": "🌨️", "snow": "❄️", "blizzard": "❄️",
    "drizzle": "🌦️", "showers": "🌧️", "light drizzle": "🌦️",
}

WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

WIND_DIR_CN = {
    "N": "北风", "NNE": "北东北风", "NE": "东北风", "ENE": "东东北风",
    "E": "东风", "ESE": "东东南风", "SE": "东南风", "SSE": "南东南风",
    "S": "南风", "SSW": "南西南风", "SW": "西南风", "WSW": "西西南风",
    "W": "西风", "WNW": "西西北风", "NW": "西北风", "NNW": "北西北风",
}

# 英文天气描述 → 中文翻译（当 lang_zh 缺失时兜底）
WEATHER_CN_MAP = {
    "sunny": "晴", "clear": "晴", "partly cloudy": "多云",
    "cloudy": "多云", "overcast": "阴天", "mist": "薄雾",
    "fog": "雾", "light rain": "小雨", "patchy rain nearby": "附近有零星小雨",
    "moderate rain": "中雨", "heavy rain": "大雨", "thunderstorm": "雷暴",
    "light snow": "小雪", "snow": "雪", "blizzard": "暴风雪",
    "drizzle": "毛毛雨", "showers": "阵雨", "light drizzle": "细雨",
    "patchy light rain": "零星小雨", "light rain shower": "小阵雨",
    "moderate or heavy rain shower": "中到大阵雨",
    "patchy light drizzle": "零星细雨",
}

# 节假日数据（简化版，用于倒计时）
FIXED_HOLIDAYS = [
    (1, 1, "元旦"), (5, 1, "劳动节"), (10, 1, "国庆节"),
]

LUNAR_HOLIDAYS_2026 = [
    (2026, 2, 17, "春节"), (2026, 4, 5, "清明节"),
    (2026, 6, 19, "端午节"), (2026, 10, 4, "中秋节"),
]


def get_weather_class(desc: str) -> str:
    """根据天气描述返回 CSS class"""
    desc_lower = desc.lower()
    for key, classes in WEATHER_CLASS_MAP.items():
        if key in desc_lower:
            return classes[0]
    return "sunny"


def get_emoji(desc: str) -> str:
    """天气描述转 emoji"""
    desc_lower = desc.lower()
    for key, emoji in WEATHER_EMOJI.items():
        if key in desc_lower:
            return emoji
    return "🌤️"


def get_wind_cn(direction: str, speed_kmh: int) -> str:
    """风向风速转中文"""
    cn_dir = WIND_DIR_CN.get(direction, direction)
    if speed_kmh < 12:
        level = "微风"
    elif speed_kmh < 20:
        level = "和风"
    elif speed_kmh < 29:
        level = "清风"
    else:
        level = "强风"
    return f"{cn_dir}{level}"


def get_mood(min_temp: int, max_temp: int, desc: str) -> str:
    """根据天气给心情 emoji"""
    desc_lower = desc.lower()
    avg = (min_temp + max_temp) // 2

    if "thunder" in desc_lower or "heavy rain" in desc_lower:
        return "😅"
    if "rain" in desc_lower or "drizzle" in desc_lower:
        return "🙂"
    if avg >= 35:
        return "🥵"
    if avg <= 0 or "snow" in desc_lower:
        return "🥶"
    if "sunny" in desc_lower or "clear" in desc_lower:
        if 18 <= avg <= 28:
            return "😊"
        elif avg > 28:
            return "😐"
        else:
            return "😌"
    return "🌤️"


def get_clothing_tips(min_temp: int, max_temp: int, desc: str, humidity: int, wind: int) -> list:
    """获取穿衣建议"""
    tips = []
    avg = (min_temp + max_temp) // 2

    if avg <= 0:
        tips.append("🧣 羽绒服+保暖内衣")
    elif avg <= 10:
        tips.append("🧥 厚外套+毛衣")
    elif avg <= 20:
        tips.append("👔 夹克+长袖")
    elif avg <= 25:
        tips.append("👕 长袖衬衫")
    elif avg <= 30:
        tips.append("🩳 短袖短裤")
    else:
        tips.append("🥵 防晒+遮阳伞")

    desc_lower = desc.lower()
    if any(w in desc_lower for w in ["rain", "drizzle", "shower", "thunder"]):
        tips.append("☂️ 记得带伞")

    if wind >= 29:
        tips.append("💨 风大注意")

    if humidity >= 90:
        tips.append("💦 湿度高")
    elif humidity <= 40:
        tips.append("🧴 空气干燥")

    if max_temp - min_temp >= 10:
        tips.append(f"🌡️ 温差{max_temp - min_temp}°C")

    return tips


def find_next_rest(target_date: datetime) -> tuple:
    """找到下一个休息日"""
    for i in range(1, 365):
        check = target_date + timedelta(days=i)
        weekday = check.weekday()
        if weekday >= 5:
            return i, f"距离周末还有{i}天"
        for hy, hm, hd, hname in LUNAR_HOLIDAYS_2026:
            if check.year == hy and check.month == hm and check.day == hd:
                return i, f"距离{hname}还有{i}天"
    return 0, ""


def fetch_weather(city: str) -> dict:
    """从 wttr.in 获取天气 JSON"""
    from urllib.parse import quote
    encoded_city = quote(city)
    url = f"https://wttr.in/{encoded_city}?format=j1&lang=zh"
    result = subprocess.run(
        ["curl", "-s", "--max-time", "20", url],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)


def render_card(data: dict, mode: str, output_path: str, city: str):
    """渲染天气卡片"""
    now = datetime.now(BJ_TZ)

    if mode == "today":
        day_data = data["weather"][0]
        date_text = f"{now.month}月{now.day}日"
        weekday = WEEKDAY_NAMES[now.weekday()]
    else:
        day_data = data["weather"][1]
        tmr = now + timedelta(days=1)
        date_text = f"{tmr.month}月{tmr.day}日"
        weekday = WEEKDAY_NAMES[tmr.weekday()]

    date_obj = datetime.strptime(day_data["date"], "%Y-%m-%d").replace(tzinfo=BJ_TZ)
    max_temp = int(day_data["maxtempC"])
    min_temp = int(day_data["mintempC"])
    avg_temp = (max_temp + min_temp) // 2

    # 主天气（取中午时段，优先中文，fallback 英文翻译）
    noon_hour = day_data["hourly"][4]  # 12:00
    noon_desc_list = noon_hour.get("lang_zh", [])
    if noon_desc_list and noon_desc_list[0].get("value"):
        main_weather = noon_desc_list[0]["value"]
    else:
        en_desc = noon_hour["weatherDesc"][0]["value"]
        main_weather = WEATHER_CN_MAP.get(en_desc.lower(), en_desc)
    main_emoji = get_emoji(main_weather)
    weather_class = get_weather_class(main_weather)

    # 风力
    avg_wind = sum(int(h["windspeedKmph"]) for h in day_data["hourly"]) // len(day_data["hourly"])
    wind_dir = noon_hour["winddir16Point"]
    wind_text = f"{WIND_DIR_CN.get(wind_dir, wind_dir)} {avg_wind}km/h"

    # 湿度
    avg_humidity = sum(int(h["humidity"]) for h in day_data["hourly"]) // len(day_data["hourly"])

    # 日出日落
    astro = day_data["astronomy"][0]

    # 心情
    mood = get_mood(min_temp, max_temp, main_weather)

    # 逐时段
    hourly_items = []
    current_hour = now.hour if mode == "today" else 0
    for h in day_data["hourly"]:
        hour = int(h["time"]) // 100
        temp = h["tempC"]
        desc_list = h.get("lang_zh", [])
        if desc_list and desc_list[0].get("value"):
            desc = desc_list[0]["value"]
        else:
            en_desc = h["weatherDesc"][0]["value"]
            desc = WEATHER_CN_MAP.get(en_desc.lower(), en_desc)
        emoji = get_emoji(desc)
        humidity = h["humidity"]
        is_now = (mode == "today" and hour == current_hour)
        now_class = " now" if is_now else ""
        hourly_items.append(f'''
          <div class="hour-item{now_class}">
            <div class="hour-time">{hour:02d}:00</div>
            <div class="hour-emoji">{emoji}</div>
            <div class="hour-temp">{temp}°</div>
            <div class="hour-humidity">💧{humidity}%</div>
          </div>''')

    # 生活建议
    tips = get_clothing_tips(min_temp, max_temp, main_weather, avg_humidity, avg_wind)
    tips_html = ""
    if tips:
        tips_items = "".join(f'<div class="tip-item">{tip}</div>' for tip in tips)
        tips_html = f'''
  <div class="tips">
    <div class="tips-title">💡 生活建议</div>
    {tips_items}
  </div>'''

    # 特殊提示（周末/节假日）
    special_note = ""
    if date_obj.weekday() >= 5:
        special_note = f'<div class="special-note">🎉 今天周末，好好休息！</div>'
    elif date_obj.weekday() == 4:
        special_note = '<div class="special-note">🎉 周五啦！明天就周末了 🍻</div>'

    # 倒计时
    rest_days, rest_text = find_next_rest(date_obj)
    countdown_html = ""
    if rest_days > 0 and not special_note:
        countdown_html = f'<div class="countdown">📅 {rest_text}</div>'

    # 读取模板
    template_path = Path(__file__).parent.parent / "templates" / "weather_card.html"
    template = template_path.read_text(encoding="utf-8")

    # 填充模板
    html = template.replace("${weather_class}", weather_class)
    html = html.replace("${city}", city)
    html = html.replace("${main_emoji}", main_emoji)
    html = html.replace("${date_text}", date_text)
    html = html.replace("${weekday}", weekday)
    html = html.replace("${special_note_html}", special_note + countdown_html)
    html = html.replace("${weather_desc}", main_weather)
    html = html.replace("${max_temp}", str(max_temp))
    html = html.replace("${min_temp}", str(min_temp))
    html = html.replace("${avg_temp}", str(avg_temp))
    html = html.replace("${mood}", mood)
    html = html.replace("${hourly_items}", "".join(hourly_items))
    html = html.replace("${tips_html}", tips_html)
    html = html.replace("${wind}", wind_text)
    html = html.replace("${humidity}", str(avg_humidity))
    html = html.replace("${sunrise}", astro["sunrise"])
    html = html.replace("${sunset}", astro["sunset"])

    # 写入临时 HTML
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        tmp_path = f.name

    # Playwright 截图
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 390, 'height': 800}, device_scale_factor=2)
            page.goto(f'file://{tmp_path}')
            page.wait_for_timeout(500)

            # 获取实际高度，精确裁剪到 390px 宽
            height = int(page.evaluate('document.body.scrollHeight'))
            page.set_viewport_size({'width': 390, 'height': height})
            page.wait_for_timeout(200)
            page.screenshot(path=output_path, clip={'x': 0, 'y': 0, 'width': 390, 'height': height})
            browser.close()
    finally:
        os.unlink(tmp_path)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="天气卡片渲染")
    parser.add_argument("--city", required=True, help="城市名（必填）")
    parser.add_argument("--mode", choices=["today", "tomorrow"], default="tomorrow")
    parser.add_argument("--output", default=os.path.expanduser("~/.hermes/cache/weather_card.png"))
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    try:
        data = fetch_weather(args.city)
        output = render_card(data, args.mode, args.output, args.city)
        print(output)
    except Exception as e:
        print(f"❌ 渲染失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
