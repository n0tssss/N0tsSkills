# 抖音续火花 (douyin-streak-renewer)

自动发送"自动续火花啦！"到抖音聊天，保持火花不灭。

## 功能

- 支持多对话批量发送
- 通过 Kimi Webbridge 控制真实浏览器
- 自动验证消息是否发送成功
- 失败自动重试（最多 3 次）
- 可配置执行频率（建议每天凌晨执行）

## 工作原理

1. 打开抖音网页版聊天页面
2. 逐个点击配置的对话
3. 发送"自动续火花啦！"
4. 验证消息是否出现在聊天记录中
5. 失败则重试

## 首次使用

### 1. 配置联系人

编辑 `scripts/streak.py` 修改联系人列表：

```python
CONVERSATIONS = [
    "宝宝呢",
    "小笨蛋宝宝1号",
    "小笨蛋宝宝2号",
]
```

名称使用 `includes()` 匹配，支持部分匹配。

### 2. 环境要求

- Kimi Webbridge 守护进程运行中
- Edge 浏览器扩展已连接
- 抖音网页版已登录
- 目标对话在聊天列表中可见

### 3. 验证配置

```bash
python3 ~/.hermes/scripts/streak.py
```

## 使用

```bash
# 手动执行
python3 ~/.hermes/scripts/streak.py

# 创建定时任务（示例：每天 00:00）
hermes cron create \
  --script streak.py \
  --schedule "0 0 * * *" \
  --no-agent \
  --name "douyin-streak"
```

## 故障排除

### 消息方向检测

正确的 class 名：`MessageItemTextisFromMe`

```javascript
// 正确：检测消息是否是自己发的
const containers = Array.from(document.querySelectorAll('[class*=MessageItemTextcontainer]'));
containers.map(m => {
  const isSelf = (m.className||'').includes('isFromMe');
  return (isSelf ? '[ME]' : '[THEM]') + ' ' + m.innerText?.trim();
});
```

### 多对话匹配陷阱

当一个名称匹配多个对话时（如"小笨蛋宝宝"匹配1号和2号），必须使用 `filter()` + 索引选择：

```python
# 正确：点击第idx个匹配
const matches = items.filter(e => title.includes(name));
const el = matches[idx];
```

### 非断行空格

抖音名称中的空格是 `\xa0`（char 160），不是普通空格，用 `includes()` 而不是 `===`。

## 常见问题

- **日志显示成功但用户说没发**：必须用浏览器打开 `douyin.com/chat?isPopup=1` 实际验证聊天记录
- **对话名称匹配**："小笨蛋宝宝"会同时匹配1号和2号，脚本通过 `idx` 参数区分
