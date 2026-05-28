---
name: douyin-streak-renewer
description: |
  Daily Douyin streak renewer — sends "自动续火花啦！" to configured conversations at midnight using Kimi Webbridge.
  Uses a Python script (scripts/streak.py) to call the Kimi Webbridge HTTP API directly, no LLM reasoning needed per run.
trigger: Cron job runs daily at 00:00
---

# Douyin Streak Renewer

Sends "自动续火花啦！" to a list of Douyin chat conversations daily at midnight via the Kimi Webbridge daemon.

## How it works

The `scripts/streak.py` script:
1. Opens `https://www.douyin.com/chat?isPopup=1` via Kimi Webbridge navigate
2. For each configured conversation name, clicks the conversation item in the list
3. Fills and sends "自动续火花啦！" via the contenteditable input
4. **Verifies** the message actually appeared in the chat (checks `isFromMe` class)
5. If verification fails, retries up to 3 times
6. Closes the session

## Configuration

Edit `scripts/streak.py` to change the `CONVERSATIONS` list:

```python
CONVERSATIONS = [
    "宝宝呢",
    "小笨蛋宝宝",
]
```

Names use `includes()` matching, so you can use a partial name.

## Requirements

- Kimi Webbridge daemon running (`~/.kimi-webbridge/bin/kimi-webbridge status`)
- Browser extension connected (`extension_connected: true`)
- Douyin.com logged in with the target conversations in the chat list
- Edge must be open or script will auto-launch it with the extension

## Cron job setup

```bash
hermes cron create \
  --script streak.py \
  --schedule "0 0 * * *" \
  --no-agent \
  --name "douyin-streak"
```

Script must be in `~/.hermes/scripts/`.

## Troubleshooting

### 用户说"没发"但日志显示成功（重要！）\n脚本报告 ✅ 不代表消息真的送达了。**特别是多对话匹配场景**，脚本可能报告发送成功但实际重复发送到了同一个对话。\n\n**诊断步骤**：\n1. 用 Kimi Webbridge 打开 `https://www.douyin.com/chat?isPopup=1`\n2. 逐个点击每个对话，检查聊天记录\n3. 用 evaluate 查询最近消息，确认时间戳是否与执行时间匹配\n4. 如果确实没发，手动补发\n\n### ⚠️ 消息方向检测（验证用）\n**正确的 class 名**: `MessageItemTextisFromMe`（不是 self/right/mine）\n```javascript\n// 正确：检测消息是否是自己发的\nconst containers = Array.from(document.querySelectorAll('[class*=MessageItemTextcontainer]'));\ncontainers.map(m => {\n  const isSelf = (m.className||'').includes('isFromMe');\n  return (isSelf ? '[ME]' : '[THEM]') + ' ' + m.innerText?.trim();\n});\n```\n\n**错误的检测方式**（会导致所有消息都被标记为 [THEM]）：\n```javascript\n// ❌ 错误：self/right/mine 这些关键词不存在\nclass.includes('self') || class.includes('right') || class.includes('mine')\n```

### 常见问题
- **对话名称匹配**: "小笨蛋宝宝" 用 `includes()` 匹配，会同时匹配 1号和 2号。脚本通过 `idx` 参数区分第几个匹配项。

### ⚠️ 多对话匹配陷阱：重复发送同一对话
**问题**: 当一个名称匹配多个对话时（如"小笨蛋宝宝"匹配1号和2号），`click_conversation` 如果总是点击第一个匹配项，会导致：
- 发送给1号 → 1号移到列表顶部 → 再次点击第一个匹配 → 又点了1号 → 2号被跳过
- 脚本报告 `✅ 小笨蛋宝宝 #2` 但实际没有发送给2号

**根因**: 抖音聊天列表按最近消息排序，发送后对话会移到顶部，`find()` 始终返回第一个匹配。

**修复**: `click_conversation(name, idx)` 函数必须使用 `filter()` + 索引选择，而不是 `find()`：
```python
# 错误：总是点第一个
const el = items.find(e => title.includes(name));

# 正确：点击第idx个匹配
const matches = items.filter(e => title.includes(name));
const el = matches[idx];
```

调用时传入循环变量：
```python
for idx in range(match_count):
    click_result = click_conversation(name, idx)  # 不是 name, 0
```

**验证方法**: 执行后用浏览器检查每个对话的聊天记录，确认最后一条消息时间戳。
- **非断行空格**: 抖音名称中的空格是 `\xa0`（char 160），不是普通空格。用 `includes()` 而不是 `===`。
- **页面未加载**: 抖音聊天页需要等几秒才加载完列表，脚本有 sleep 等待。

## Reference files

- `references/kimi-webbridge-react-click.md` — 用 evaluate + MouseEvent 点击 React 页面元素的通用技巧
- `references/edge-auto-launch.md` — 扩展未连接时自动启动 Edge 的设置模式
