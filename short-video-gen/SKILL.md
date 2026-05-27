---
name: short-video-gen
description: 短视频生成 — 确认基本参数后 AI 自主创意发挥
argument-hint: "<视频主题描述>"
level: 4
---

# 短视频生成

用户给主题，AI 做视频。唯一流程：**缺参数就问，不缺就开始**。

## 工作目录

```
D:\视频生成\
  .config.json
  .history.json
  <project>/
    index.html
    rendered.mp4
    素材/
```

## 输出

默认 1920×1080，用户可指定竖屏/方形/4:3 等。

---

## 开始前：确认基本参数

用户调用时，检查以下参数。缺了就用 `AskUserQuestion` 问，不缺直接开始：

- **时长** — 用户没说 + 配置没有 → 问（15s / 30s / 60s / AI 判断）
- **视觉风格** — 用户没说 + 配置没有 → 问（10 种配色方案任选）
- **视频比例** — 用户没说 → 按默认 1920×1080，不追问
- **BGM** — 按配置，不追问
- **TTS** — 按配置，不追问

用户可以说"你帮我决定"跳过任何问题。

---

## 做视频

确认参数后，AI 自主完成：

1. **研究** — 网站用 kimi-webbridge 实地访问，开源仓库读 README，搜集真实数据和素材
2. **脚本** — 确定时长、场景、每屏内容、台词
3. **设计** — 确定配色方案和视觉方向
4. **实现** — 写 HTML + CSS + GSAP，渲染输出

所有创意决策（场景数量、布局、动画、装饰、图片使用、是否放链接）由 AI 根据题材自行判断。

## 工具

- **kimi-webbridge** — 浏览器实地调研网站、搜索下载图片素材
- **HyperFrames** — HTML 渲染视频（`npx hyperframes init` / `npm run render`）
- **FFmpeg** — 合成 BGM
- **小米 MiMo TTS** — 配音（可选，需 API Key）

## 视觉参考

10 种配色方案可供选用，也可以自由发挥：

| 风格 | 底色 | 主色 |
|------|------|------|
| 赛博朋克 | `#0a0a12` | 紫+青绿渐变 |
| 极简白 | `#fafafa` | 蓝紫渐变 |
| 暗金 | `#0c0c0c` | 金色渐变 |
| 活力橙蓝 | `#0f0f1a` | 橙蓝渐变 |
| 暗夜绿 | `#0a0f0a` | 绿青渐变 |
| 霓虹粉紫 | `#0f0a14` | 粉紫渐变 |
| 纯黑暴力 | `#000` | 纯白+红点缀 |
| 暖橘日落 | `#1a100a` | 橙粉渐变 |
| 冰川蓝 | `#f0f5fa` | 深蓝渐变 |
| 红黑警戒 | `#0a0000` | 红色渐变 |

常用装饰 CSS：网格背景、对角斜线、虚线圆环、发光文字、玻璃态卡片、渐变边框、角落装饰线、轮廓字、暗角、Ken Burns。

常用文字效果：逐字弹入、模糊reveal、clipPath reveal、text-shadow 发光。

## 首次配置

`.config.json` 不存在时，打印选项等用户输入：

```
🎬 短视频生成 — 首次配置

【1. 默认时长】 [0] 每次 AI 判断 [1] 15s [2] 30s [3] 60s [4] 自定义
【2. 背景音乐】 [1] 自动合成 [2] 不加 [3] 手动提供 MP3
【3. 默认视觉】 [1]~[10] 选一个 [0] 每次 AI 推荐
【4. TTS 配音】 [1] 小米 MiMo [2] 暂不加
```

## 环境

Node.js ≥ 22 · FFmpeg · HyperFrames · kimi-webbridge

## HyperFrames 规范

`class="clip"`、`data-start/duration/track-index`、GSAP `paused: true` 注册到 `window.__timelines`、orb 不同 track-index、场景结束 `tl.set()` hard kill、BGM 用 `src="bgm.mp3"`、不用 `Math.random()`/`Date.now()`
