---
name: short-video-gen
description: 视频制作 — 调研→审核→脚本→生成→配音 完整工业化流水线
argument-hint: "<视频想法>"
level: 4
---

# 视频制作

用户提出想法 → AI 自主完成调研/审核/分镜/生成/TTS → 输出视频。

**关键流程：先给出建议让用户决策，再执行。**

---

## 工作目录

```
D:\视频生成\<project>/
  素材/              # 截图、图片、Logo、BGM
  compositions/      # 分镜片段（子合成用于复杂项目）
  index.html         # 主合成
  rendered.mp4       # 最终视频
```

---

## 完整流程

```
用户提想法
    │
    ▼
Stage 0  选题评估   竞品调研 → 选题分析 → 用 AskUserQuestion 确认
    │
    ▼
Stage 1  参数确认   给出建议 → AskUserQuestion 让用户决策（时长/风格/比例/BGM/TTS）
    │
    ▼
Stage 2  信息收集   kimi-webbridge 深度调研 + 素材收集 + 数据核实
    │
    ▼
Gate 2   素材审核   ≥5文件？有logo？有主视觉？数据有来源？→ 不通过打回
    │
    ▼
Stage 3  脚本设计   分镜表 + 画面描述 + 素材关联 + 视觉动画方案
    │
    ▼
Gate 3   方案审核   一条主线？前3秒钩子？素材全覆盖？布局多样性？→ 不通过打回
    │
    ▼
Stage 4  实现渲染   HTML + CSS + GSAP + 可用组件 → check → render
    │
    ▼
Gate 4   最终审核   技术质量 + 内容质量 → 不通过回修
    │
    ▼
Stage 5  音频合成   TTS 配音（可选）+ BGM 混音
    │
    ▼
rendered.mp4
```

---

## Stage 0: 选题评估

### 0.1 竞品调研

WebSearch 搜同类内容，了解：
- 同类最高播放量（天花板在哪）
- 常见角度和切入点
- 评论区的未满足需求
- 我们的差异化空间

### 0.2 选题分析

- **一句话卖点**：看完能获得什么？
- **目标受众**：谁看？什么场景看？
- **差异化**：和同类有什么不同？
- **流量潜力**：话题性强？适合传播？
- **执行可行性**：素材能收集到吗？

### 0.3 用户确认

用 `AskUserQuestion` 给出分析并确认方向。

---

## Stage 1: 参数确认

**先给出建议，再用 AskUserQuestion 让用户决策。**

必须确认的参数（缺什么问什么）：

```
视频时长：[建议具体值] → [1] AI判断 [2] 15s [3] 30s [4] 60s [5] 自定义
视觉风格：[建议具体风格] → 10种配色可选 + AI推荐
视频比例：[建议具体比例] → [1] 1920×1080 横屏 [2] 1080×1920 竖屏 [3] 其他
BGM：[1] 自动合成 [2] 不加 [3] 手动提供
TTS：[1] 不加 [2] 小米 MiMo（需 API Key）
```

确认完毕后打印汇总。

---

## Stage 2: 信息收集

按题材类型深度调研：

**网站/产品/服务**（kimi-webbridge）：
- 首页、关于、功能、定价、联系——逐个页面截图
- 提取真实数据（用户数、年份、slogan）
- 下载 logo，记录所有可用文案
- 有 Demo 的打开截图

**开源项目**：
- 读 README，提取功能/技术栈/场景
- 下载官方截图/Logo（assets/目录）
- 获取 Stars/Forks/License 等真实数据

**游戏/影视/文化**：搜 Google Images/壁纸站，≥5张不同高清图

**数据核实**：所有数字必须有来源，不确定的不用。

---

### Gate 2: 素材审核

```
□ 素材 ≥5 个不同文件？
□ 不同内容方向？（不是同一张图反复用）
□ 有高清主视觉？（能全屏铺满的）
□ 有 logo？
□ 关键数据有来源？
□ 现有素材能覆盖每个场景？
```

不通过标注缺什么，打回 Stage 2。

---

## Stage 3: 脚本设计

产出分镜表：

| # | 时间 | 素材 | 画面描述 | 画面文字 | 动画/特效 |
|---|------|------|---------|---------|----------|
| 1 | 0-4s | hero.png | 全屏蒙层+大字 | "X" | 模糊reveal |

要求：
- 前3秒有钩子（反常识/大数字/痛点/好奇）
- 每场景用不同素材
- 相邻场景布局不重复
- 每个场景指定所用素材

---

### Gate 3: 方案审核

```
□ 一句话说得清视频讲什么吗？
□ 前3秒够强吗？
□ 每个场景都指定了素材？
□ 场景布局有变化（≥3种）？
□ 符合用户确认的参数和方向？
```

不通过标注改哪里，打回 Stage 3。

---

## Stage 4: 实现渲染

### 视觉特效系统（按需使用）

HyperFrames 提供 50+ 现成组件：

```bash
npx hyperframes add <block-name>
```

**推荐组件**：

| 场景类型 | 推荐组件 |
|---------|---------|
| 开场/标题 | `kinetic-slam`、`glitch-rgb`、`neon-glow` |
| 数据展示 | `data-chart`、`shimmer-sweep`、`texture-mask-text` |
| 关键词强调 | `emoji-pop`、`particle-burst`、`highlight` |
| 过渡转场 | 20+ 种 shader transitions 可选 |
| 截图/产品 | `parallax-zoom`、`parallax-unzoom` |
| 结尾 CTA | `logo-outro`、`pill-karaoke` |

### 官方项目文件和流程（来自 HyperFrames launch video）

复杂项目建议维护以下文档（参考官方团队做法）：

```
SCRIPT.md      # 配音脚本（VO 原文，供 TTS/录音用）
STORYBOARD.md  # 分镜表 + 视觉描述
HANDOFF.md     # 每次迭代的生产日志（改了什么、为什么、验证方法）
```

**脚本格式示例：**
```markdown
## Spoken VO

Spoken lines only. This block feeds TTS verbatim.
```
Imagine you could make videos like this.
Your agent already can — just give it HyperFrames.
Open source. HTML in, video out.
```
```

### 官方已验证的子合成时间线修复

HyperFrames 官方团队在 launch video 中遇到了完全相同的黑帧问题。
**根因：** 框架由 `timeline.duration()` 决定可见性，不是 `data-duration`。
**修复：** 每个子合成末尾填充时间线。

```javascript
tl.to({}, { duration: MASTER_SLOT_DURATION }, 0);
window.__timelines["composition-id"] = tl;
```

**验证方法**（官方提供，在浏览器控制台运行）：
```javascript
const p = document.querySelector('hyperframes-player');
const iw = p.shadowRoot.querySelector('iframe').contentWindow;
Object.fromEntries(Object.entries(iw.__timelines).map(([k,v]) => [k, +v.duration().toFixed(4)]));
```

任何 `timeline.duration() < master slot data-duration` 的合成都会出现黑帧。

### HyperFrames 组件库（62 个块 + 23 个组件）

安装：`npx hyperframes add <name>`

**过渡效果块（33 个）** — 场景切换，4s 时长：
`flash-through-white` `cinematic-zoom` `glitch` `cross-warp-morph` `domain-warp-dissolve`
`ridged-burn` `ripple-waves` `gravitational-lens` `swirl-vortex` `light-leak` `whip-pan`
`transitions-blur` `transitions-dissolve` `transitions-distortion` `transitions-push`

**文字动效组件（16 个）** — 叠加在子合成中：
`caption-kinetic-slam`(全屏大字交替进入) `caption-particle-burst`(关键词粒子爆炸)
`caption-glitch-rgb`(RGB故障) `caption-neon-glow`(霓虹辉光) `caption-matrix-decode`(矩阵解码)
`caption-emoji-pop`(表情弹出) `caption-weight-shift`(字重动画)

**电影级叠加组件（4 个）** — 直接 paste 到 HTML：
`grain-overlay`(胶片颗粒) `vignette`(暗角晕影) `shimmer-sweep`(光泽扫描)
`texture-mask-text`(纹理遮罩文字)

**数据可视化块（8 个）**：`data-chart` `world-map` `us-map` `flowchart`
**社交/UI 叠加块（11 个）**：`instagram-follow` `tiktok-follow` `yt-lower-third` `x-post`
**VFX 特效块（10 个）**：`vfx-shatter` `vfx-portal` `vfx-magnetic` `logo-outro`

### 子合成（复杂项目标准模式）

多场景视频应拆分为独立合成文件，用 `data-composition-src` 编排。

**推荐项目结构：**
```
project/
├── index.html            # 编排器：音频 + 子合成插槽 + 空时间线
├── compositions/
│   ├── scene-1-hook.html
│   ├── scene-2-features.html
│   └── scene-3-cta.html
├── assets/
│   └── fonts/
└── renders/
```

**父合成（index.html）：**
```html
<div id="master" data-composition-id="master" data-start="0" data-duration="60"
     data-width="1080" data-height="1920">
  <audio src="bgm.mp3" class="clip" data-start="0" data-duration="60"
         data-track-index="40" data-has-audio="true" data-volume="0.06"></audio>

  <div data-composition-id="scene1" data-composition-src="compositions/scene-1-hook.html"
       data-start="0" data-duration="8" data-track-index="1"></div>
  <div data-composition-id="scene2" data-composition-src="compositions/scene-2-features.html"
       data-start="8" data-duration="12" data-track-index="1"></div>
</div>

<script>
window.__timelines = window.__timelines || {};
window.__timelines["master"] = gsap.timeline({ paused: true });  // 空时间线
</script>
```

**子合成（compositions/scene-1-hook.html）：**
```html
<template id="scene1-template">
<div data-composition-id="scene1" data-width="1080" data-height="1920"
     data-start="0" data-duration="8">
  <!-- 场景内容 -->
</div>
<style>
  [data-composition-id="scene1"] { /* 作用域样式 */ }
</style>
</template>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script>
window.__timelines = window.__timelines || {};
var tl = gsap.timeline({ paused: true });
tl.from("#title", { opacity: 0, y: 80, duration: 0.6 }, 0);

// ⚠️ 关键：填充时间线到 data-duration，否则框架会提前隐藏（黑帧）
tl.to({}, { duration: 8 }, 0);
window.__timelines["scene1"] = tl;
</script>
```

### 子合成时间线规则 ⚠️

HyperFrames 根据 GSAP `.duration()` 决定可见性。如果 `tl.duration()` < `data-duration`，框架提前 `visibility:hidden` → **黑帧**。

```javascript
// ✅ 填充到完整插槽时长（两种方式均可）
tl.to({}, { duration: 8 }, 0);  // 空对象补间
tl.set({}, {}, 8 * 30);         // 或延长到最后一帧（30fps）

// ❌ tl.duration()=4s, 父级 data-duration=8 → 后4s黑屏
```

验证（浏览器控制台）：
```javascript
Object.fromEntries(
  Object.entries(window.__timelines).map(([k,v]) => [k, +v.duration().toFixed(4)])
);
```

### GSAP 缓动函数映射

用自然语言描述动画感觉：

| 描述 | GSAP easing | 适合场景 |
|-----|------------|---------|
| 流畅 | `power2.out` | 默认，通用入场 |
| 利落 | `power4.out` | 快速切换、数据变化 |
| 弹性 | `back.out(1.5)` | 数字弹出、CTA 按钮 |
| 弹簧 | `elastic.out(1,0.3)` | 强调、趣味元素 |
| 戏剧性 | `expo.out` | 大字标题、reveal |
| 梦幻 | `sine.inOut` | 淡入淡出、呼吸动画 |

### 快速迭代工作流

```bash
npx hyperframes render --quality draft   # 草稿模式（CRF 28，1-3min）
ffmpeg -ss 5 -i renders/draft.mp4 -frames:v 1 frame_5s.png  # 检查某一帧
npx hyperframes render                   # 最终渲染
```

### 音频轨道编号约定

| 范围 | 用途 |
|-----|------|
| 0 | 画外音/VO |
| 40+ | BGM |
| 80+ | 音效 |
| 90+ | 字幕叠加 |

### 嵌入方法

```html
<!-- 组件：直接贴到 #root 内 -->
<div id="grain-overlay"><div class="grain-texture"></div></div>
<div id="hf-vignette"></div>

<!-- 块：data-composition-src 嵌入子合成 -->
<div data-composition-src="compositions/flash-through-white.html"
     data-duration="4" data-width="1080" data-height="1920"></div>
```

### 使用经验

- `grain-overlay` + `vignette` 是"必加"组合，零配置提升观感
- caption 组件在子合成中使用
- 过渡块默认 1920×1080，竖屏要改成 1080×1920
- `timeline_track_too_dense` 警告说明该拆子合成了

## 竖屏 (9:16) 设计原则 ⚠️ 关键

竖屏 (1080×1920) 和横屏 (1920×1080) 是完全不同的设计范式。
**绝对不能把横屏缩小当竖屏用。**

### 核心理念

| 横屏思维 ❌ | 竖屏思维 ✅ |
|-----------|-----------|
| 左右分栏 | 上下堆叠 |
| 水平多列卡片 | 单列/全幅卡片 |
| 文字 40-48px | 文字 80-145px |
| 高信息密度 | 每屏少但大 |
| 横向滑动入场 | 纵向滑动入场 |
| 元素左右排列 | 元素纵向排列 |

### 安全区（Safe Zones）

竖屏视频在 TikTok/Reels/Shorts 会被 UI 遮挡：

```
┌──────────────────────┐
│  ░░░ 顶部遮挡 260px ░░░│  ← 头像、用户名、标题
│                        │
│   ┌──────────────┐   │
│   │  核心安全区    │   │  ← x:90~990, y:260~1660
│   │  ~900×1400px  │   │     所有关键内容放这里
│   └──────────────┘   │
│                        │
│  ░░░ 底部遮挡 340px ░░░│  ← 字幕、点赞、操作按钮
└──────────────────────┘
```

- **顶部 260px 不要放关键信息**
- **底部 340px 只放字幕/CTA**
- **核心内容限制在 900×1400 区域内**
- **左右侧让出 90px**

### 竖屏排版规范

| 元素 | 字号 | 行高 | 每行字数 | 最多行数 |
|-----|------|------|---------|---------|
| **主标题（冲击力）** | 110-145px | 110% | ≤10字 | 2行 |
| **章节标题** | 80-96px | 120% | ≤15字 | 2行 |
| **副标题/标签** | 55-65px | 120% | ≤20字 | 1行 |
| **正文/描述** | 40-55px | 120% | ≤20字 | 3行 |
| **底部字幕** | 40-55px | 120% | ≤25字 | 2行 |
| **标注数字** | 130-180px | 90% | ≤6字 | 1行 |

### 竖屏布局模式（取代横屏方案）

竖屏只有垂直空间可用，所有布局应围绕"从上往下看"设计：

```
[类型 A] 全屏视觉 + 居中大字        — 开场/钩子/CTA
┌─────────────────┐
│   全屏背景图      │
│                   │
│    大字标题       │  ← 居中
│                   │
└─────────────────┘

[类型 B] 上标题 + 下内容             — 功能/描述/产品
┌─────────────────┐
│  标签/小标题      │  ← y:100-260
├─────────────────┤
│                   │
│  图片/截图         │  ← 核心区域
│  (全幅宽度)        │
│                   │
├─────────────────┤
│  底部说明文字      │  ← 安全区内
└─────────────────┘

[类型 C] 垂直卡片列表（单列）        — 功能罗列/卖点
┌─────────────────┐
│  标题             │
├─────────────────┤
│  ▓ 卡片 1         │  ← 全幅宽度
├─────────────────┤
│  ▓ 卡片 2         │
├─────────────────┤
│  ▓ 卡片 3         │
└─────────────────┘

[类型 D] 大数字 + 底部说明           — 数据冲击
┌─────────────────┐
│                   │
│                   │
│    130,000        │  ← 超大字居中
│                   │
│    GitHub Stars    │  ← 小字说明
│                   │
└─────────────────┘

[类型 E] 垂直对比（上/下分栏）       — 对比
┌─────────────────┐
│  ❌ 传统方案      │
│  缺点描述...      │
├─────────────────┤
│  ✅ 我们的方案     │
│  优点描述...      │
└─────────────────┘
```

### 竖屏 GSAP 动画规则

- **优先 y 轴动画**（竖向滑动），x 轴在窄画布上很挤
- 禁止 `x: -100` 这种横向大幅位移
- `x: -30` 以内的微偏移可以接受（icon/标签入场）
- **zoom/scale 放大**在竖屏效果好
- **blur in**（模糊变清晰）适合大字标题
- 元素从下方滑入比从侧面更自然

```javascript
// ✅ 竖屏推荐
tl.from("#title", { opacity: 0, y: 80, duration: 0.6 });
tl.from("#number", { opacity: 0, scale: 0.4, duration: 0.5 });
tl.from("#subtitle", { opacity: 0, filter: "blur(10px)", duration: 0.5 });

// ❌ 竖屏避免
// tl.from("#card", { x: -200, ... });  // 画布才1080宽，200px太猛
```

### 素材使用规则

- 背景图/视频必须 `object-fit: cover` 填满 1080×1920
- 产品截图/Logo 最多占画幅 60% 宽度（~650px），居中
- 人物/主体置于画面中心（上下居中）
- 图片下方留足够空间给文字

### 复杂项目建议用子合成

场景较多时用 `data-composition-src` 拆分：

```html
<div id="scene1" data-composition-id="intro" data-composition-src="compositions/intro.html"
     data-start="0" data-duration="10" data-track-index="1"></div>
```

### 字幕/文字叠加

使用底部 caption + backdrop-filter 更专业：

```css
.caption {
  position: absolute; bottom: 80px; left: 50%; transform: translateX(-50%);
  padding: 12px 28px; border-radius: 10px;
  background: rgba(0,0,0,0.55); backdrop-filter: blur(8px);
  color: rgba(255,255,255,0.92); font-size: 40px;
}
```

### 渲染

```bash
npm run check && npm run render
cp renders/*.mp4 ../rendered.mp4
```

---

### Gate 4: 最终审核

```
□ 正常播放？无卡帧/花屏/黑屏？
□ 内容符合设计方案？
□ 作为观众，觉得好看吗？原因？
```

不通过回修。

---

## Stage 5: 音频合成

### 配音（TTS）

用 `tts-generate.js` 模块自动生成。

1. 从脚本台词提取 **tts-lines.json**：
   ```json
   [{ "text": "每次聊天都像第一次见面", "start": 0.5, "duration": 2.5 }]
   ```

2. 执行生成（默认 edge-tts，免费）：
   ```bash
   pip install edge-tts
   node tts-generate.js
   ```

3. 生成的 `<audio>` 标签粘贴到 `index.html` 的 `#root` 中

edge-tts 可用中文语音：`zh-CN-YunyangNeural`（男声专业）
也可用小米 MiMo（需 API Key）：`node tts-generate.js --mimo`

**注意**：每个 audio 标签必须有唯一 `id`，否则渲染器不会发现 → 静音。

### BGM

```bash
# 合成简单 BGM（FFmpeg 正弦波 + 粉噪）
ffmpeg -f lavfi -i "sine=frequency=220:duration=60" -f lavfi -i "anoisesrc=d=60:c=pink:a=0.02" \
  -filter_complex "[0]volume=0.3[a];[1]volume=0.5[b];[a][b]amix=inputs=2:duration=first" \
  assets/bgm.mp3
```

BGM 音量 `data-volume="0.06-0.08"`，VO 音量 `data-volume="1.0"`。

---

## 实践经验

- **数据核实**：去官方渠道确认，不编数字
- **HyperFrames 可见性**：`data-start/duration` 管显示/隐藏，GSAP 只做动画
- **浮点精度**：duration = nextStart - currentStart - 0.02
- **必跑 check**：检查 overlap/溢出
- **素材先行**：素材不够不写 HTML，否则=幻灯片
- **块组件**：`npx hyperframes add <name>` 安装现成特效块
- **竖屏横屏不通用**：竖屏是独立设计范式，不能把横屏缩小当竖屏用
- **场景转场**：白闪过渡最简单高效——`tl.to(opacity:0) → tl.set(flash) → tl.to(flash:0) + tl.set(hard kill)`
- **动效点缀**：关键数字用 `boxShadow` 脉冲发光，截图用 `filter:brightness()` 呼吸，关键词用金色渐变 + `textShadow` 辉光
- **GSAP 硬重置**：每个 clip 结束边界必须加 `tl.set()`，否则非线性 seek 会留脏状态
- **`flash-overlay` 要素**：需要 `class="clip"` + `data-track-index`（高于 scenes 低于 overlays）

## 工具 & 环境

- **kimi-webbridge**（浏览器调研）：`127.0.0.1:10086`，需要 Chrome 扩展（ID: `fldmhceldgbpfpkbgopacenieobmligc`）
- **HyperFrames**：`npx hyperframes`（init / preview / check / render / add）
- **FFmpeg**：BGM 合成（正弦波 + 粉噪）
- **小米 MiMo TTS**：`api.xiaomimimo.com/v1`，OpenAI 兼容接口
- **Node.js** ≥ 22
- **代理**（Clash）：`127.0.0.1:7897`

## HyperFrames 速查

```html
<div class="clip" data-start="0" data-duration="5" data-track-index="10">
```
- GSAP `paused:true` → `window.__timelines["main"]`
- orb 不同 track-index
- `tl.set()` hard kill
- 不用 `Math.random()` / `Date.now()`
