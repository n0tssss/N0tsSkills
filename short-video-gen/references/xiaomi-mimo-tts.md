# 小米 MiMo TTS API 调用

小米 MiMo TTS 使用 chat completions API 格式，不是标准的 /audio/speech 端点。

## API 端点

```
POST https://api.xiaomimimo.com/v1/chat/completions
```

## 认证

```
Authorization: Bearer <API_KEY>
```

## 请求格式

```json
{
  "model": "mimo-v2.5-tts",
  "messages": [
    {
      "role": "user",
      "content": "用清晰自然的中文女声，语速适中"
    },
    {
      "role": "assistant",
      "content": "要合成的文字内容"
    }
  ],
  "audio": {
    "format": "wav",
    "voice": "Chloe"
  }
}
```

**关键点**：
- 文字放在 `assistant` 角色的 `content` 里，不是 `user`
- `user` 角色放风格指令（可选）
- `voice` 可选：Chloe 等内置声音

## 可用模型

| 模型 | 用途 |
|------|------|
| mimo-v2.5-tts | 内置声音合成 |
| mimo-v2.5-tts-voicedesign | 文字描述自定义声音 |
| mimo-v2.5-tts-voiceclone | 基于音频样本克隆声音 |

## 返回格式

返回 JSON，音频数据在 `choices[0].message.audio.data`（base64 编码）。

## Python 调用示例

```python
import base64, json, os
from urllib.request import Request, urlopen

key = os.environ.get("XIAOMI_API_KEY")
data = json.dumps({
    "model": "mimo-v2.5-tts",
    "messages": [
        {"role": "user", "content": "用温暖自然的中文女声"},
        {"role": "assistant", "content": "要合成的文字"}
    ],
    "audio": {"format": "wav", "voice": "Chloe"}
}).encode()

req = Request("https://api.xiaomimimo.com/v1/chat/completions",
              data=data,
              headers={"Authorization": f"Bearer {key}",
                       "Content-Type": "application/json"})
resp = json.loads(urlopen(req).read())
audio_b64 = resp["choices"][0]["message"]["audio"]["data"]
with open("output.wav", "wb") as f:
    f.write(base64.b64decode(audio_b64))
```
