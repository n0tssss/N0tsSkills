---
name: short-video-gen
description: 短视频生成 — 通用短视频生成工具，支持多种视觉风格和文案风格，一键生成 4:3 横屏 + 3:4 竖屏视频
argument-hint: "<视频主题描述>"
level: 4
---

# 短视频生成

通用短视频生成工具。用户描述主题/内容，工具自动生成 4:3 横屏 + 3:4 竖屏两版视频。

## 工作目录

```
D:\视频生成\
  .config.json          # 风格配置
  .history.json         # 生成记录
  <project-name>\       # 每个视频一个子目录
    43-横屏.mp4
    34-竖屏.mp4
```

## 使用方式

**首次使用** → 自动进入配置向导（打印全部选项，等用户输入序号）。

**后续使用** → 用户描述视频主题，直接用已保存的风格配置生成。

---

## 首次配置

当 `.config.json` 不存在时，一次性输出以下内容，然后等待用户输入：

```
🎬 短视频生成 — 首次配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1. 视频时长】
  [1] 15 秒 — 短平快
  [2] 20 秒
  [3] 30 秒 — 展示更充分
  [4] 自定义

【2. 背景音乐】
  [1] 自动合成 — FFmpeg 生成电子氛围音轨
  [2] 不加 BGM — 纯画面
  [3] 手动提供 — 放 MP3 到 D:\视频生成\bgm\ 目录，每次随机抽

【3. 视觉配色】
  [1] 赛博朋克 — 深紫+霓虹蓝+青绿，深色底
  [2] 极简白 — 白底+蓝色强调，干净清爽
  [3] 暗金科技 — 黑底+金色+琥珀渐变，高端
  [4] 活力橙蓝 — 橙+蓝对比，醒目大胆
  [5] 暗夜绿 — 深绿+荧光绿，黑客终端风
  [6] 霓虹粉紫 — 品红+电紫，潮流年轻
  [7] 纯黑暴力 — 纯黑底+白字+红点缀，极致冲击
  [8] 暖橘日落 — 暖橙+粉渐变，温暖质感
  [9] 冰川蓝 — 极浅蓝白+深蓝，冷冽专业
  [10] 红黑警戒 — 黑底+正红，紧迫高能

【4. 文案叙事风格】
  [1] 一句话暴力 — 短句砸脸，≤20 字 punchline
  [2] 痛点轰炸 — 先制造焦虑再给解药
  [3] 颠覆认知 — 否定常识再反转

【5. 内容侧重】
  [1] 核心亮点 — 聚焦 3-4 个 killer feature
  [2] 功能罗列 — 尽可能多展示功能标签

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
请回复你的选择，格式如：1-1, 2-1, 3-2, 4-1, 5-1
（即第1题选1、第2题选1、第3题选2...）
```

用户回复后，解析序号，写入配置，并输出确认信息：

```
✅ 配置已保存！
   · 30 秒 · 自动 BGM · 极简白 · 颠覆认知 · 核心亮点

现在你可以告诉我：想做什么主题的短视频？
比如："介绍 GitHub 今天最热的开源工具"
或者："介绍一下 vscode 的 10 个实用插件"
```

## 配置写入格式

```json
{
  "duration": 30,
  "bgm": "auto",
  "visualStyle": "minimal",
  "copyStyle": "subvert",
  "featureMode": "highlights",
  "createdAt": "2026-05-26"
}
```

`visualStyle` 映射：1→cyberpunk, 2→minimal, 3→dark-gold, 4→vibrant, 5→terminal, 6→neon-pop, 7→brutal, 8→sunset, 9→glacier, 10→alert

`copyStyle` 映射：1→one-liner, 2→pain-first, 3→subvert

---

## 日常使用

用户调用时描述主题（如"介绍今天的 GitHub 热门工具"、"给 vscode 做个介绍视频"）。

### Step 1: 理解需求

从用户描述中提取：
- 视频要讲什么？
- 有没有指定的目标（如某个网站、某个仓库）？
- 需要什么素材？

如果用户说"今日 GitHub 热门工具"之类，则去 `https://github.com/trending` 找，跳过 `.history.json` 中已做过的。

### Step 2: 收集素材

优先真实素材：
1. 项目自带的截图/Demo 图/GIF → `curl` 下载
2. 项目官网/Demo 网站 → 截图
3. GitHub opengraph 预览图
4. 都没有 → 纯文字排版

### Step 3: 生成视频

创建 `D:\视频生成\<name>\43\` 和 `D:\视频生成\<name>\34\` 两个 HyperFrames 项目。

视频结构根据 `copyStyle` 选择：

**「一句话暴力」(`one-liner`)**:
| 场景 | 占比 | 内容 |
|------|------|------|
| 砸脸 | 20% | 反常识/夸张短句，最大字号 |
| 解药 | 25% | 工具名 + 真实截图，后半句形成 punchline |
| 凭什么 | 30% | 3 个 feature chip，配合截图标注 |
| 证据 | 15% | 大截图 + 数据（Stars 等） |
| 去哪 | 10% | GitHub/链接地址 |

**「痛点轰炸」(`pain-first`)**:
| 场景 | 占比 | 内容 |
|------|------|------|
| 扎心 | 20% | 痛点反问句 |
| 放大 | 15% | 痛点升级 |
| 救星 | 25% | 工具名 + 解决方案 + 截图 |
| 拆招 | 25% | 逐条展示如何解决 |
| 行动 | 15% | 链接 + 数据背书 |

**「颠覆认知」(`subvert`)**:
| 场景 | 占比 | 内容 |
|------|------|------|
| 否定 | 20% | 否定常识的大字 |
| 反转 | 15% | 翻转动画 + "其实..." |
| 真相 | 25% | 工具名 + 真相揭晓 + 真实截图 |
| 证据链 | 25% | 连续快速切换画面，模拟真实使用 |
| 记住 | 15% | 产品名 + 链接 |

### 视觉风格参数

**赛博朋克 (cyberpunk)**: 底色 `#0a0a12`，紫+青绿 orb，标题渐变色 `linear-gradient(135deg, #c084fc, #22d3ee)`，标签 `rgba(34,211,238,0.12)` 底 + `#22d3ee` 文字，CTA `linear-gradient(135deg, #7c3aed, #06b6d4)`

**极简白 (minimal)**: 底色 `#fafafa`，极淡 orb，标题 `#1a1a2e` 或 `linear-gradient(135deg, #4f46e5, #7c3aed)`，标签 `#eef2ff` 底 + `#4f46e5` 文字，CTA `#4f46e5`

**暗金科技 (dark-gold)**: 底色 `#0c0c0c`，金色+琥珀 orb，标题渐变色 `linear-gradient(135deg, #fbbf24, #f59e0b)`，标签 `rgba(251,191,36,0.12)` 底 + `#fbbf24` 文字，CTA `linear-gradient(135deg, #b45309, #d97706)`

**活力橙蓝 (vibrant)**: 底色 `#0f0f1a`，橙+蓝 orb，标题渐变色 `linear-gradient(135deg, #f97316, #3b82f6)`，标签 `rgba(249,115,22,0.15)` 底 + `#fb923c` 文字，CTA `linear-gradient(135deg, #ea580c, #2563eb)`

**暗夜绿 (terminal)**: 底色 `#0a0f0a`，绿+青 orb，标题渐变色 `linear-gradient(135deg, #22c55e, #06b6d4)`，标签 `rgba(34,197,94,0.12)` 底 + `#4ade80` 文字，CTA `linear-gradient(135deg, #15803d, #0891b2)`

**霓虹粉紫 (neon-pop)**: 底色 `#0f0a14`，品红+紫 orb，标题渐变色 `linear-gradient(135deg, #ec4899, #a855f7)`，标签 `rgba(236,72,153,0.12)` 底 + `#f472b6` 文字，CTA `linear-gradient(135deg, #db2777, #7c3aed)`

**纯黑暴力 (brutal)**: 底色 `#000000`，极暗灰 orb，标题 `#ffffff` 纯白无渐变最大字重，标签 `rgba(255,255,255,0.06)` 底 + `#fff` + `#ef4444` 强调，CTA `#ef4444`

**暖橘日落 (sunset)**: 底色 `#1a100a`，暖橙+粉 orb，标题渐变色 `linear-gradient(135deg, #f97316, #ec4899)`，标签 `rgba(249,115,22,0.12)` 底 + `#fb923c` 文字，CTA `linear-gradient(135deg, #c2410c, #be185d)`

**冰川蓝 (glacier)**: 底色 `#f0f5fa`，极淡蓝+白 orb，标题 `#1e3a5f` 或渐变色 `linear-gradient(135deg, #1e40af, #0369a1)`，标签 `#dbeafe` 底 + `#1d4ed8` 文字，CTA `#1e40af`

**红黑警戒 (alert)**: 底色 `#0a0000`，红+暗红 orb，标题渐变色 `linear-gradient(135deg, #ef4444, #dc2626)`，标签 `rgba(239,68,68,0.12)` 底 + `#f87171` 文字，CTA `linear-gradient(135deg, #b91c1c, #991b1b)`

### 通用规则

- 不展示安装命令，只展示能干嘛
- 标题 ≥80px，副标题 ≥36px，正文 ≥28px
- 场景切换 0.25s 淡出 + 0.3s 淡入，元素弹出间隔 0.12-0.2s
- 每屏 ≤15 字，一屏一个核心信息
- 优先用真实截图/图片，纯文字是最后手段
- 最后必须放链接地址（大字 CTA）
- 文案动词开头，口语化，像广告不像文档

### Step 4: 渲染

```bash
export PATH="/d/software/nvm/v22.21.1:$PATH"
cd "D:/视频生成/<name>/43" && npm run render
cd "D:/视频生成/<name>/34" && npm run render
```

渲染完成后复制到项目根目录：
```bash
cp 43/renders/*.mp4 ../43-横屏.mp4
cp 34/renders/*.mp4 ../34-竖屏.mp4
```

### Step 5: 记录

在 `.history.json` 追加生成记录（含主题、时间、输出目录），避免重复。

---

## 环境要求

- Node.js ≥ 22（`nvm use 22`）
- FFmpeg（`scoop install ffmpeg`）
- HyperFrames（`npx hyperframes init` 自动下载）

## 实现注意

- 符合 HyperFrames 规范：`class="clip"`、`data-start`、`data-duration`、`data-track-index`
- GSAP timeline `paused: true`，注册到 `window.__timelines`
- 背景 orb 用不同 track-index 避免 overlap
- 每场景结束加 `tl.set()` hard kill
- 不使用 `Math.random()` 或 `Date.now()`
- 竖屏 `1080×1440`，横屏 `1600×1200`
- BGM 复制到项目内用 `src="bgm.mp3"`
- 输出命名为 `43-横屏.mp4` 和 `34-竖屏.mp4`
