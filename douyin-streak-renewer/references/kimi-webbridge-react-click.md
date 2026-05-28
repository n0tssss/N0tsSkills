# 用 evaluate + MouseEvent 点击 React 页面元素

Kimi Webbridge 的 `click` 工具使用 `el.click()` （合成事件，`isTrusted=false`），
许多 React 页面（如抖音聊天）不响应这种点击。

## 解决方案：通过 evaluate 派发原生 MouseEvent

```python
# Python 中的 JavaScript 代码片段
js = (
    "(() => {"
    "const el = document.querySelector('.conversationConversationItemwrapper');"
    "const r = el.getBoundingClientRect();"
    "el.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, clientX: r.left + 10, clientY: r.top + 30}));"
    "el.dispatchEvent(new MouseEvent('mouseup',   {bubbles: true, clientX: r.left + 10, clientY: r.top + 30}));"
    "el.dispatchEvent(new MouseEvent('click',     {bubbles: true, clientX: r.left + 10, clientY: r.top + 30}));"
    "return 'OK';"
    "})()"
)
```

## 关键要点

- `isTrusted=false` 仍是合成事件，但 MouseEvent 序列（mousedown→mouseup→click）比单独 `el.click()` 更接近真实交互
- `clientX`/`clientY` 需要落在元素内部有效区域
- 元素的 `scrollIntoView()` 可以确保元素在视口内
- 这个方法对 Douyin 等 React 应用有效，但对严格检查 `event.isTrusted` 的网站（银行、验证码）仍然无效

## evaluate 与 f-string 注意事项

在 Python f-string 中嵌入 JS 时，`{` 和 `}` 需要转义为 `{{` 和 `}}`。
更安全的做法是使用字符串拼接（+）代替 f-string，如上面的示例。
