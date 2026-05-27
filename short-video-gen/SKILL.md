---
name: short-video-gen
description: 短视频生成 — 分析→脚本→设计→实现，AI 自主创意发挥
argument-hint: "<视频主题描述>"
level: 4
---

# 短视频生成

**AI 自主创意，用户只给主题。** 时长、风格、节奏、布局全部由 AI 根据题材决定。

## 工作目录

```
D:\视频生成\
  .config.json
  .history.json
  <project>/
    分析报告.md
    视频脚本.md
    设计稿.md
    素材/
    index.html
    rendered.mp4
```

## 输出

默认 1920×1080 横屏，用户可以说"竖屏"、"方的"、"都要"等。

---

## 核心原则

1. **AI 做创意决策** — 时长、风格、配色、节奏、布局都是你决定，不需要逐项问用户
2. **每个场景必须有图** — 真实照片/截图/封面，不是纯文字卡片
3. **最后必须放链接/地址** — 让观众知道去哪
4. **文案口语化** — 每屏简短有力，像广告不像文档

---

## 参数补全

只问必须问的（用 `AskUserQuestion`），其余 AI 自行决定：

- **用户已经说了的**：主题、时长、风格方向 → 直接用
- **没说的但配置有的**：BGM、默认视觉 → 直接用配置
- **没说的且配置没有的**：视觉风格、视频比例 → 根据题材自己推荐 2-4 个方向问一下
- **AI 自己定的**：时长（15-90s 根据内容复杂度）、场景数量、布局、动画、装饰

---

## 流水线

### Phase 1: 分析

深度理解主题。网站/Web 产品用 kimi-webbridge 实地访问。搜集：一句话定位、核心卖点、真实数据、可用图片。

### Phase 2: 脚本

按确定的时长写脚本。格式：时间、布局类型、画面描述、画面文字、台词(TTS)、动画方向。

### Phase 3: 设计

确定配色、字体层级、关键帧布局。用视觉风格参数速查表选色，可以在此基础上自由发挥。

### Phase 4: 实现

写 HTML + CSS + GSAP。**每场景必须有 `<img>` 或 CSS background-image**，图片优先用 kimi-webbridge 浏览器搜索下载，备选 Steam CDN / GitHub og-image / 官网截图。

渲染：
```bash
npm run check && npm run render
cp renders/*.mp4 ../rendered.mp4
```

---

## 图片收集

优先用 kimi-webbridge 浏览器搜索实际图片，不要只靠猜 URL：

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
# 去 Google Images / 壁纸站 / Steam 商店搜图
# evaluate 提取图片 src → curl 下载到素材/
```

---

## 视觉参考（建议，非强制）

### 装饰元素

CSS 代码片段可供选用：网格背景、对角斜线、虚线圆环、点阵、发光文字、玻璃态卡片、渐变边框、角落装饰线、轮廓字背景。

### 文字效果

超大字号(≥100px)、渐变文字、模糊reveal、clipPath reveal、字间距拉开(letter-spacing)、text-shadow 发光。

### 图片处理

全屏 `object-fit: cover` + 暗色蒙层(`rgba(0,0,0,0.55-0.8)`)、Ken Burns 微缩放、暗角(vignette)、相框边框。

### 场景过渡

淡入淡出、缩放穿越、滑动切换、模糊切换。

---

## 视觉风格参数速查

| 风格 | 底色 | 标题渐变 | 标签 | CTA |
|------|------|---------|------|-----|
| 赛博朋克 | `#0a0a12` | `#c084fc→#22d3ee` | `rgba(34,211,238,0.12)` + `#22d3ee` | `#7c3aed→#06b6d4` |
| 极简白 | `#fafafa` | `#4f46e5→#7c3aed` | `#eef2ff` + `#4f46e5` | `#4f46e5` |
| 暗金 | `#0c0c0c` | `#fbbf24→#f59e0b` | `rgba(251,191,36,0.12)` + `#fbbf24` | `#b45309→#d97706` |
| 活力橙蓝 | `#0f0f1a` | `#f97316→#3b82f6` | `rgba(249,115,22,0.15)` + `#fb923c` | `#ea580c→#2563eb` |
| 暗夜绿 | `#0a0f0a` | `#22c55e→#06b6d4` | `rgba(34,197,94,0.12)` + `#4ade80` | `#15803d→#0891b2` |
| 霓虹粉紫 | `#0f0a14` | `#ec4899→#a855f7` | `rgba(236,72,153,0.12)` + `#f472b6` | `#db2777→#7c3aed` |
| 纯黑暴力 | `#000` | `#fff` 纯白 | `rgba(255,255,255,0.06)` + `#fff` | `#ef4444` |
| 暖橘日落 | `#1a100a` | `#f97316→#ec4899` | `rgba(249,115,22,0.12)` + `#fb923c` | `#c2410c→#be185d` |
| 冰川蓝 | `#f0f5fa` | `#1e40af→#0369a1` | `#dbeafe` + `#1d4ed8` | `#1e40af` |
| 红黑警戒 | `#0a0000` | `#ef4444→#dc2626` | `rgba(239,68,68,0.12)` + `#f87171` | `#b91c1c→#991b1b` |

## 环境

- Node.js ≥ 22 · FFmpeg · HyperFrames (`npx hyperframes init`)
- kimi-webbridge（浏览器搜图用）

## HyperFrames 规范

`class="clip"`、`data-start/duration/track-index`、GSAP `paused: true` 注册到 `window.__timelines`、orb 不同 track-index、场景结束 `tl.set()` hard kill、BGM 用 `src="bgm.mp3"`、不用 `Math.random()`/`Date.now()`
