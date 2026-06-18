#!/usr/bin/env python3
"""
天气数据采集脚本 — 输出原始 JSON，供 AI 翻译后再渲染。
用法: python3 fetch_weather_data.py --city "上海金山" --mode today
"""
import json
import sys
import subprocess
import argparse
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

BJ_TZ = timezone(timedelta(hours=8))

WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

WIND_DIR_CN = {
    "N": "北风", "NNE": "北东北风", "NE": "东北风", "ENE": "东东北风",
    "E": "东风", "ESE": "东东南风", "SE": "东南风", "SSE": "南东南风",
    "S": "南风", "SSW": "南西南风", "SW": "西南风", "WSW": "西西南风",
    "W": "西风", "WNW": "西西北风", "NW": "西北风", "NNW": "北西北风",
}

FIXED_HOLIDAYS = [
    (1, 1, "元旦"), (5, 1, "劳动节"), (10, 1, "国庆节"),
]
LUNAR_HOLIDAYS_2026 = [
    (2026, 2, 17, "春节"), (2026, 4, 5, "清明节"),
    (2026, 6, 19, "端午节"), (2026, 10, 4, "中秋节"),
]


def find_next_rest(target_date):
    for i in range(1, 365):
        check = target_date + timedelta(days=i)
        if check.weekday() >= 5:
            return i, f"距离周末还有{i}天"
        for hy, hm, hd, hname in LUNAR_HOLIDAYS_2026:
            if check.year == hy and check.month == hm and check.day == hd:
                return i, f"距离{hname}还有{i}天"
    return 0, ""


def main():
    parser = argparse.ArgumentParser(description="天气数据采集")
    parser.add_argument("--city", required=True, help="城市名（必填）")
    parser.add_argument("--mode", choices=["today", "tomorrow"], default="today")
    args = parser.parse_args()

    now = datetime.now(BJ_TZ)
    encoded_city = quote(args.city)
    url = f"https://wttr.in/{encoded_city}?format=j1&lang=zh"

    result = subprocess.run(
        ["curl", "-s", "--max-time", "20", url],
        capture_output=True, text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        print(json.dumps({"error": "wttr.in 请求失败"}))
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(json.dumps({"error": "JSON 解析失败"}))
        sys.exit(1)

    if args.mode == "today":
        day_data = data["weather"][0]
        date_text = f"{now.month}月{now.day}日"
        weekday = WEEKDAY_NAMES[now.weekday()]
    else:
        day_data = data["weather"][1]
        tmr = now + timedelta(days=1)
        date_text = f"{tmr.month}月{tmr.day}日"
        weekday = WEEKDAY_NAMES[tmr.weekday()]

    max_temp = int(day_data["maxtempC"])
    min_temp = int(day_data["mintempC"])
    avg_temp = (max_temp + min_temp) // 2

    # 收集所有时段的英文描述（需要 AI 翻译）
    hourly = []
    for h in day_data["hourly"]:
        hour = int(h["time"]) // 100
        en_desc = h["weatherDesc"][0]["value"]
        hourly.append({
            "hour": f"{hour:02d}:00",
            "temp": h["tempC"],
            "humidity": h["humidity"],
            "weather_en": en_desc,  # 英文描述，需要 AI 翻译
        })

    # 主天气取中午
    noon_desc = day_data["hourly"][4]["weatherDesc"][0]["value"]

    # 风力
    avg_wind = sum(int(h["windspeedKmph"]) for h in day_data["hourly"]) // len(day_data["hourly"])
    wind_dir = day_data["hourly"][4]["winddir16Point"]
    wind_text = f"{WIND_DIR_CN.get(wind_dir, wind_dir)} {avg_wind}km/h"

    # 湿度
    avg_humidity = sum(int(h["humidity"]) for h in day_data["hourly"]) // len(day_data["hourly"])

    # 日出日落
    astro = day_data["astronomy"][0]

    # 节假日
    date_obj = datetime.strptime(day_data["date"], "%Y-%m-%d").replace(tzinfo=BJ_TZ)
    rest_days, rest_text = find_next_rest(date_obj)

    output = {
        "city": args.city,
        "mode": args.mode,
        "date_text": date_text,
        "weekday": weekday,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "avg_temp": avg_temp,
        "weather_en": noon_desc,  # 需要 AI 翻译
        "wind": wind_text,
        "humidity": avg_humidity,
        "sunrise": astro["sunrise"],
        "sunset": astro["sunset"],
        "rest_days": rest_days,
        "rest_text": rest_text,
        "hourly": hourly,  # 每个时段都有 weather_en 需要翻译
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
