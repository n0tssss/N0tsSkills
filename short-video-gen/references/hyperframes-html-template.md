# HyperFrames HTML 模板要点

渲染失败最常见的原因是 HTML 模板缺少必要属性。以下是从多次渲染失败中总结的必填项。

## 根元素必须有

```html
<div id="composition" data-composition-id="唯一ID" data-width="1080" data-height="1920" data-start="0">
```

- `data-composition-id` — 唯一标识，不能缺
- `data-width` / `data-height` — 像素尺寸，不能缺
- `data-start="0"` — 必须从 0 开始

## window.__timelines 注册

Timeline 名字必须和 `data-composition-id` 一致：

```javascript
window.__timelines = {};
window.__timelines["hermes-intro"] = tl;  // 必须匹配 data-composition-id
```

❌ 错误：注册为 "main" 但 composition-id 是 "hermes-intro"

## window.__hf 暴露

```javascript
window.__hf = {
  duration: 40,  // 总时长（秒）
  seek: function(time) {
    tl.seek(time);
  }
};
```

HyperFrames 会等 `window.__hf` 就绪，超时 45 秒会报错。

## 音频元素

```html
<audio id="bgm" src="配音.wav" data-start="0" data-duration="40"></audio>
```

必须有 `data-start` 和 `data-duration`，否则 HyperFrames 不管理播放。

## 场景元素

每个场景需要：
- 唯一 `id`
- 初始 `opacity: 0`（由 GSAP 控制显示）
- 不要用 `clip` class（除非你真的需要 clip 效果）

```css
.scene { opacity: 0; }
```

## GSAP Timeline 模式

```javascript
const tl = gsap.timeline({ paused: true });
tl.to('#scene-1', { opacity: 1, duration: 0.5 })
  .to('#scene-1', { opacity: 0, duration: 0.5, delay: 3 })
  // ... 更多场景
window.__timelines["composition-id"] = tl;
```

## 常见渲染错误

| 错误 | 原因 | 修复 |
|------|------|------|
| `root_missing_composition_id` | 缺 data-composition-id | 加到根元素 |
| `root_missing_dimensions` | 缺 data-width/height | 加到根元素 |
| `timeline_id_mismatch` | timelines 注册名和 id 不匹配 | 统一名称 |
| `window.__hf not ready` | 没暴露 __hf 或 duration/seek 缺失 | 加 __hf 对象 |
| `media_missing_data_start` | audio 没 data-start | 加 data-start="0" |
