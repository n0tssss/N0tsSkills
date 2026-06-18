# wttr.in API 参考

## 基础用法
```
# 纯文本（一行摘要）
curl -s "https://wttr.in/{城市}?format=%l:+%c+%t+%h+%w+%p"

# ASCII 天气图（3天预报）
curl -s "https://wttr.in/{城市}?format=v2&lang=zh"

# JSON 完整数据（逐3小时预报）
curl -s "https://wttr.in/{城市}?format=j1&lang=zh"
```

## JSON 结构 (format=j1)
```json
{
  "weather": [                    // 数组，[0]=今天, [1]=明天, [2]=后天
    {
      "date": "2026-06-01",
      "maxtempC": "25",
      "mintempC": "20",
      "avgtempC": "23",
      "hourly": [                 // 8个时段: 0,3,6,9,12,15,18,21点
        {
          "time": "1200",         // HHMM 格式字符串
          "tempC": "25",
          "humidity": "83",
          "windspeedKmph": "18",
          "winddir16Point": "ESE", // 16方位
          "weatherDesc": [{"value": "Patchy rain nearby"}],
          "lang_zh": [{"value": "附近小雨"}]  // lang=zh 时有中文描述
        }
      ],
      "astronomy": [{
        "sunrise": "04:54 AM",
        "sunset": "06:53 PM"
      }]
    }
  ]
}
```

## 注意事项
- 中文城市名需 URL 编码：`urllib.parse.quote("上海金山")`
- Python urllib 在 macOS 上可能有 SSL 问题，用 `subprocess` + `curl` 更稳定
- `lang=zh` 参数让 weatherDesc 返回中文，但不一定所有城市都有中文描述
- wttr.in 是免费服务，无 API key，但有速率限制
