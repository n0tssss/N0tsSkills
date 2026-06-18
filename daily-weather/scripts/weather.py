#!/usr/bin/env python3
"""
天气查询脚本 — 查询指定城市天气，输出格式化通知
用法:
  python3 weather.py --city "北京" --mode tomorrow   # 明天天气
  python3 weather.py --city "上海" --mode today      # 今天天气
  python3 weather.py --city "Shanghai+Jinshan" --mode tomorrow  # 英文城市名
"""
import json
import sys
import argparse
import urllib.request
from datetime import datetime, timezone, timedelta

BJ_TZ = timezone(timedelta(hours=8))

# 中国法定节假日 (月, 日) — 固定日期部分
# 农历节日每年不同，这里放公历固定节日 + 近几年的农历节日估算
FIXED_HOLIDAYS = [
    (1, 1, "元旦"),
    (5, 1, "劳动节"),
    (10, 1, "国庆节"),
    (10, 2, "国庆节"),
    (10, 3, "国庆节"),
    (10, 4, "国庆节"),
    (10, 5, "国庆节"),
    (10, 6, "国庆节"),
    (10, 7, "国庆节"),
]

# 农历节日近似日期 (年, 月, 日) — 需要每年更新
LUNAR_HOLIDAYS_2026 = [
    (2026, 2, 17, "春节"),
    (2026, 2, 18, "春节"),
    (2026, 2, 19, "春节"),
    (2026, 2, 20, "春节"),
    (2026, 2, 21, "春节"),
    (2026, 2, 22, "春节"),
    (2026, 2, 23, "春节"),
    (2026, 4, 5, "清明节"),
    (2026, 6, 19, "端午节"),
    (2026, 6, 20, "端午节"),
    (2026, 6, 21, "端午节"),
    (2026, 10, 4, "中秋节"),
]

# 放假日调休上班日 (需要每年更新)
WORKDAYS_OVERRIDE = set()  # (year, month, day) — 调休补班日

WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

WEATHER_EMOJI = {
    "Sunny": "☀️", "Clear": "🌙", "Partly Cloudy": "⛅",
    "Cloudy": "☁️", "Overcast": "☁️", "Mist": "🌫️",
    "Fog": "🌫️", "Light Rain": "🌦️", "Patchy rain nearby": "🌦️",
    "Moderate Rain": "🌧️", "Heavy Rain": "🌧️", "Thunderstorm": "⛈️",
    "Light Snow": "🌨️", "Snow": "❄️", "Blizzard": "❄️",
    "Drizzle": "🌦️", "Showers": "🌧️", "Light Drizzle": "🌦️",
}

WIND_DIR_CN = {
    "N": "北风", "NNE": "北东北风", "NE": "东北风", "ENE": "东东北风",
    "E": "东风", "ESE": "东东南风", "SE": "东南风", "SSE": "南东南风",
    "S": "南风", "SSW": "南西南风", "SW": "西南风", "WSW": "西西南风",
    "W": "西风", "WNW": "西西北风", "NW": "西北风", "NNW": "北西北风",
}


def fetch_weather(city: str, max_retries: int = 3) -> dict:
    """从 wttr.in 获取天气 JSON（带重试）"""
    from urllib.parse import quote
    import subprocess
    import time
    encoded_city = quote(city)
    url = f"https://wttr.in/{encoded_city}?format=j1&lang=zh"
    last_err = None
    for attempt in range(1, max_retries + 1):
        result = subprocess.run(
            ["curl", "-s", "--max-time", "20", url],
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        last_err = result.stderr or f"empty response (attempt {attempt})"
        if attempt < max_retries:
            time.sleep(2 * attempt)
    raise RuntimeError(f"curl failed after {max_retries} attempts: {last_err}")


def get_day_type(date_obj: datetime) -> str:
    """判断某天是工作日、周末还是节假日"""
    y, m, d = date_obj.year, date_obj.month, date_obj.day

    # 调休补班日优先
    if (y, m, d) in WORKDAYS_OVERRIDE:
        return "workday"

    # 农历节日
    for hy, hm, hd, hname in LUNAR_HOLIDAYS_2026:
        if y == hy and m == hm and d == hd:
            return f"holiday:{hname}"

    # 固定公历节日
    for hm, hd, hname in FIXED_HOLIDAYS:
        if m == hm and d == hd:
            return f"holiday:{hname}"

    # 周末
    weekday = date_obj.weekday()
    if weekday >= 5:
        return "weekend"

    return "workday"


def find_next_rest(target_date: datetime) -> tuple[int, str]:
    """找到距离下一个休息日（周末或节假日）的天数"""
    for i in range(1, 365):
        check = target_date + timedelta(days=i)
        day_type = get_day_type(check)
        if day_type != "workday":
            if day_type.startswith("holiday:"):
                name = day_type.split(":")[1]
                return i, f"距离{name}还有{i}天"
            else:  # weekend
                return i, f"距离周末还有{i}天"
    return 0, ""


def find_next_holiday(target_date: datetime) -> tuple[int, str]:
    """找到距离下一个法定节假日的天数"""
    for i in range(1, 365):
        check = target_date + timedelta(days=i)
        day_type = get_day_type(check)
        if day_type.startswith("holiday:"):
            name = day_type.split(":")[1]
            return i, f"🎉 距离{name}还有{i}天"
    return 0, ""


def get_emoji_for_weather(desc: str) -> str:
    """天气描述转 emoji"""
    for key, emoji in WEATHER_EMOJI.items():
        if key.lower() in desc.lower():
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
    return f"{cn_dir}{level}({speed_kmh}km/h)"


def format_hourly(hourly_data: list) -> str:
    """格式化逐时段预报"""
    lines = []
    for h in hourly_data:
        hour = int(h["time"]) // 100
        temp = h["tempC"]
        desc = h.get("lang_zh", [{}])
        desc_text = desc[0]["value"] if desc else h["weatherDesc"][0]["value"]
        emoji = get_emoji_for_weather(desc_text)
        humidity = h["humidity"]
        lines.append(f"  {hour:02d}:00 {emoji} {temp}°C 💧{humidity}%")
    return "\n".join(lines)


def get_clothing_advice(min_temp: int, max_temp: int, weather_desc: str, humidity: int, wind_kmh: int) -> list[str]:
    """根据天气给出穿衣建议"""
    tips = []
    avg = (min_temp + max_temp) // 2

    # 温度穿衣
    if avg <= 0:
        tips.append("🧣 羽绒服+保暖内衣，冻手冻脚的天别逞强")
    elif avg <= 5:
        tips.append("🧥 厚外套+毛衣，出门裹严实点")
    elif avg <= 10:
        tips.append("🧥 薄羽绒/厚外套，里面穿卫衣刚好")
    elif avg <= 15:
        tips.append("👔 夹克/风衣+长袖，早晚温差大带件外套")
    elif avg <= 20:
        tips.append("👕 长袖衬衫/薄外套，舒适温度随便穿")
    elif avg <= 25:
        tips.append("👕 短袖/T恤就行，怕冷的带件薄衫")
    elif avg <= 30:
        tips.append("🩳 短袖短裤安排上，轻薄透气为主")
    elif avg <= 35:
        tips.append("🩲 尽量穿浅色宽松衣服，防晒+透气")
    else:
        tips.append("🥵 能不出门别出门，出门必须防晒霜+遮阳伞")

    # 雨天
    desc_lower = weather_desc.lower()
    rain_words = ["rain", "drizzle", "shower", "thunder", "storm", "雨"]
    if any(w in desc_lower for w in rain_words):
        tips.append("☂️ 记得带伞！")
        if "heavy" in desc_lower or "thunder" in desc_lower:
            tips.append("⚡ 有大雨/雷暴，尽量别骑车")

    # 风力
    if wind_kmh >= 29:
        tips.append("💨 风大，女生长发扎起来，裙子慎穿")

    # 湿度
    if humidity >= 90:
        tips.append("💦 湿度爆表，衣服选速干面料，黏糊糊的不好受")
    elif humidity <= 40:
        tips.append("🧴 空气干燥，记得涂润唇膏和保湿")

    # 温差大
    if max_temp - min_temp >= 10:
        tips.append(f"🌡️ 温差{max_temp - min_temp}°C，早出晚归记得加衣服")

    # 高温
    if max_temp >= 35:
        tips.append("🧊 多喝水！避免午后暴晒，小心中暑")
    elif max_temp >= 33:
        tips.append("💧 多喝水，出门带瓶水")

    # 低温
    if min_temp <= 5:
        tips.append("🥶 早上出门挺冷的，能多睡会儿就多睡会儿")

    return tips


def get_mood_emoji(min_temp: int, max_temp: int, weather_desc: str) -> str:
    """根据天气给一个心情 emoji"""
    desc_lower = weather_desc.lower()
    avg = (min_temp + max_temp) // 2

    if "thunder" in desc_lower or "heavy rain" in desc_lower:
        return "😅"
    if "rain" in desc_lower or "drizzle" in desc_lower or "shower" in desc_lower:
        return "🙂"
    if avg >= 35:
        return "🥵"
    if avg <= 0:
        return "🥶"
    if "snow" in desc_lower:
        return "🥶"
    if "sunny" in desc_lower or "clear" in desc_lower:
        if 18 <= avg <= 28:
            return "😊"
        elif avg > 28:
            return "😐"
        else:
            return "😌"
    if "cloud" in desc_lower or "overcast" in desc_lower:
        return "😌"
    return "🌤️"


def format_report(weather_data: dict, mode: str) -> str:
    """生成天气报告"""
    now = datetime.now(BJ_TZ)

    if mode == "today":
        day_data = weather_data["weather"][0]
        title = f"今天 {now.strftime('%m月%d日')} {WEEKDAY_NAMES[now.weekday()]}"
    else:  # tomorrow
        day_data = weather_data["weather"][1]
        tmr = now + timedelta(days=1)
        title = f"明天 {tmr.strftime('%m月%d日')} {WEEKDAY_NAMES[tmr.weekday()]}"

    date_obj = datetime.strptime(day_data["date"], "%Y-%m-%d").replace(tzinfo=BJ_TZ)
    max_temp = day_data["maxtempC"]
    min_temp = day_data["mintempC"]

    # 主天气 — 取中午时段的天气作为代表
    noon_hour = day_data["hourly"][4]  # 12:00
    noon_desc = noon_hour.get("lang_zh", [{}])
    main_weather = noon_desc[0]["value"] if noon_desc else noon_hour["weatherDesc"][0]["value"]
    main_emoji = get_emoji_for_weather(main_weather)

    # 风力
    avg_wind = sum(int(h["windspeedKmph"]) for h in day_data["hourly"]) // len(day_data["hourly"])
    wind_dir = noon_hour["winddir16Point"]
    wind_text = get_wind_cn(wind_dir, avg_wind)

    # 湿度
    avg_humidity = sum(int(h["humidity"]) for h in day_data["hourly"]) // len(day_data["hourly"])

    # 日出日落
    astro = day_data["astronomy"][0]

    # 距离放假/周末
    rest_days, rest_text = find_next_rest(date_obj)
    holiday_days, holiday_text = find_next_holiday(date_obj)

    # 今日是否是节假日
    day_type = get_day_type(date_obj)
    special_note = ""
    if day_type == "weekend":
        special_note = "🎉 今天周末，好好休息！"
    elif day_type.startswith("holiday:"):
        hname = day_type.split(":")[1]
        special_note = f"🎉 今天是{hname}假期！"
    elif date_obj.weekday() == 4:  # Friday
        special_note = "TGIF！明天就周末了 🍻"

    # 心情 emoji
    mood = get_mood_emoji(int(min_temp), int(max_temp), main_weather)

    # 构建报告
    report_parts = [f"{main_emoji} {title} | {main_weather} {min_temp}-{max_temp}°C {mood}"]

    if special_note:
        report_parts.append(special_note)
    else:
        # 只在不是假日/周末时显示倒计时
        if rest_days > 0:
            report_parts.append(f"📅 {rest_text}")
        if holiday_days > 0 and holiday_days != rest_days:
            report_parts.append(f"{holiday_text}")

    # 逐时段
    report_parts.append("")
    report_parts.append("⏰ 逐时段:")
    report_parts.append(format_hourly(day_data["hourly"]))

    # 💡 生活建议
    tips = get_clothing_advice(
        int(min_temp), int(max_temp), main_weather, avg_humidity, avg_wind
    )
    if tips:
        report_parts.append("")
        report_parts.append("💡 小贴士:")
        for tip in tips:
            report_parts.append(f"  {tip}")

    # 底部信息
    report_parts.append("")
    report_parts.append(f"🌬️ {wind_text} | 💧 湿度 {avg_humidity}%")
    report_parts.append(f"🌅 日出 {astro['sunrise']} | 🌇 日落 {astro['sunset']}")

    return "\n".join(report_parts)


def main():
    parser = argparse.ArgumentParser(description="天气查询")
    parser.add_argument("--city", required=True, help="城市名（必填）")
    parser.add_argument("--mode", choices=["today", "tomorrow"], default="tomorrow",
                        help="查询今天还是明天")
    args = parser.parse_args()

    try:
        data = fetch_weather(args.city)
        report = format_report(data, args.mode)
        print(report)
    except Exception as e:
        print(f"❌ 天气查询失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
