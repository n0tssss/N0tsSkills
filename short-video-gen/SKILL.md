---
name: short-video-gen
description: 短视频生成 — 分析→脚本→设计→实现 四阶段流水线，丰富的视觉特效系统
argument-hint: "<视频主题描述>"
level: 4
---

# 短视频生成

四阶段流水线：**分析 → 脚本 → 设计 → 实现**。全自动执行，参数补全后一路到底。

## 工作目录

```
D:\视频生成\
  .config.json
  .history.json
  <project>/
    分析报告.md
    视频脚本.md
    设计稿.md
    素材/              # 截图、图片、BGM、配音
    index.html         # 项目文件
    rendered.mp4       # 最终视频
```

## 输出规格

**默认**：1920×1080，16:9 横屏。文件名 `rendered.mp4`。

用户可指定其他规格：
- "做个竖屏视频" → 1080×1920
- "做个方视频" → 1080×1080
- "横屏竖屏都要" → 同时输出两个
- "要 4:3 的" → 1600×1200

**不主动做双版本**，除非用户明确要求。

---

## 首次配置

`.config.json` 不存在时，一次性打印全部选项，等用户输入序号：

```
🎬 短视频生成 — 首次配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1. 默认时长】 [0] 每次自动判断 [1] 15秒 [2] 30秒 [3] 60秒 [4] 自定义
【2. 背景音乐】 [1] 自动合成 [2] 不加 [3] 手动提供 MP3
【3. 默认视觉】 [1] 赛博朋克 [2] 极简白 [3] 暗金 [4] 活力橙蓝
                [5] 暗夜绿 [6] 霓虹粉紫 [7] 纯黑暴力 [8] 暖橘日落
                [9] 冰川蓝 [10] 红黑警戒
                [0] 每次根据题材推荐（灵活）
【4. TTS 配音】  [1] 小米 MiMo TTS [2] 暂不加

回复格式：1-0, 2-1, 3-7, 4-2
```

---

## 视觉系统

### 装饰元素（每个场景至少用 2 种）

不要只放文字 + orb。每个场景至少使用以下 2 种装饰：

**几何装饰**：
```css
/* 细线网格 */
.grid-bg { background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
           background-size: 60px 60px; }

/* 对角线装饰条 */
.diagonal-stripe { position: absolute; width: 200%; height: 4px;
                   background: linear-gradient(90deg, var(--c1), var(--c2));
                   transform: rotate(-25deg); opacity: 0.3; }

/* 圆环 */
.ring { border: 2px solid rgba(255,255,255,0.08); border-radius: 50%;
        width: 400px; height: 400px; position: absolute; }

/* 虚线圆 */
.dashed-ring { border: 2px dashed rgba(255,255,255,0.06); border-radius: 50%; }

/* 点阵 */
.dot-grid { background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 30px 30px; }

/* 角落装饰线 */
.corner-lines::before, .corner-lines::after { content: ''; position: absolute; }
.corner-lines::before { top: 20px; left: 20px; width: 60px; height: 60px;
                         border-top: 2px solid var(--c1); border-left: 2px solid var(--c1); }
.corner-lines::after { bottom: 20px; right: 20px; width: 60px; height: 60px;
                        border-bottom: 2px solid var(--c1); border-right: 2px solid var(--c1); }
```

**发光效果**：
```css
.glow-text { text-shadow: 0 0 40px rgba(99,102,241,0.5), 0 0 80px rgba(99,102,241,0.2); }
.glow-box { box-shadow: 0 0 60px rgba(99,102,241,0.15), 0 20px 60px rgba(0,0,0,0.3); }
```

**高斯模糊玻璃态**：
```css
.glass { background: rgba(255,255,255,0.04); backdrop-filter: blur(20px);
         border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; }
```

**渐变边框卡片**：
```css
.gradient-border { position: relative; background: rgba(0,0,0,0.3); border-radius: 16px; }
.gradient-border::before { content: ''; position: absolute; inset: 0; border-radius: 16px;
    padding: 1px; background: linear-gradient(135deg, var(--c1), var(--c2));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude; }
```

### 文字设计

**不要只用一种字号居中排列**。混合使用：

```css
/* 超大轮廓字（作为背景纹理） */
.outline-text {
  font-size: 200px; font-weight: 900; letter-spacing: -5px;
  color: transparent; -webkit-text-stroke: 1px rgba(255,255,255,0.06);
  position: absolute; top: -40px; left: -20px; pointer-events: none;
}

/* 数字大爆炸 */
.big-number { font-size: 160px; font-weight: 900; line-height: 0.8;
              background: linear-gradient(180deg, var(--c1) 0%, transparent 100%);
              -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* 标签组倾斜排列 */
.tag-skew { transform: rotate(-2deg); display: inline-block; }

/* 字间距拉开 */
.wide { letter-spacing: 8px; text-transform: uppercase; font-size: 18px; }
```

**文字动画**（不只是 fade in）：
```js
// 逐字弹入
tl.from(".char-animate .char", { opacity: 0, y: 30, rotate: -5, duration: 0.4, stagger: 0.03, ease: "back.out(1.7)" });

// 文字从模糊到清晰
tl.from(".blur-reveal", { filter: "blur(20px)", opacity: 0, duration: 0.8, ease: "power3.out" });

// 文字剪切reveal
tl.from(".clip-reveal", { clipPath: "inset(0 100% 0 0)", duration: 0.7, ease: "power3.inOut" });
```

### 图片处理

```css
/* 图片暗角 */
.vignette::after { content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.6) 100%); }

/* 图片微微缩放（Ken Burns 效果） */
.ken-burns img { animation: kenburns 5s ease-out forwards; }
@keyframes kenburns { from { transform: scale(1); } to { transform: scale(1.08); } }

/* 图片彩色边框 */
.frame-border { border: 3px solid var(--c1); border-radius: 12px;
                box-shadow: 0 0 0 8px rgba(0,0,0,0.3), 0 20px 60px rgba(0,0,0,0.4); }

/* 双图叠加 */
.img-stack { position: relative; }
.img-stack img:last-child { position: absolute; top: 20px; left: 20px; opacity: 0.6;
                             filter: blur(2px); z-index: -1; transform: scale(0.95); }
```

### 场景布局模板（不要只用居中flex）

**A. 全屏砸脸** — 适合开场 punchline
```
┌─────────────────────────┐
│  [大号轮廓字作背景纹理]    │
│                         │
│     最大字号主标题        │
│     副标题紧接下方        │
│                         │
│  [底部几何装饰线]         │
└─────────────────────────┘
```

**B. 左图右文** — 适合截图+特性
```
┌─────────────────────────┐
│ [标签]                  │
│                         │
│ ┌──────┐  特性 1        │
│ │ 截图  │  特性 2        │
│ │      │  特性 3        │
│ └──────┘                │
│          [装饰圆环]      │
└─────────────────────────┘
```

**C. 大图铺满 + 文字叠加** — 适合证据展示
```
┌─────────────────────────┐
│                         │
│     [全屏截图/图片]      │
│                         │
│  ┌──────────────────┐   │
│  │ 半透明玻璃卡片     │   │
│  │ 大号文字 + 数据    │   │
│  └──────────────────┘   │
└─────────────────────────┘
```

**D. 分散式拼贴** — 适合功能罗列
```
┌─────────────────────────┐
│       [大标题]           │
│                         │
│  [卡片1]    [卡片2]      │
│      [卡片3]    [卡片4]  │
│  [卡片5]    [卡片6]      │
│                         │
│    [背景几何线条穿越]     │
└─────────────────────────┘
```

**E. 上下分层** — 适合教程步骤
```
┌─────────────────────────┐
│      [标题区 30%]        │
│                         │
│  1 ─────────────────    │
│  2 ─────────────────    │
│  3 ─────────────────    │
│                         │
│      [底部装饰线]        │
└─────────────────────────┘
```

### 场景过渡（不只是淡入淡出）

```js
// 缩放穿越（当前场景放大消失 → 新场景从缩小恢复）
tl.to(currElems, { scale: 1.3, opacity: 0, duration: 0.3, ease: "power2.in" });
tl.from(nextElems, { scale: 0.7, opacity: 0, duration: 0.4, ease: "power2.out" });

// 滑动切换（横移）
tl.to(currElems, { x: -80, opacity: 0, duration: 0.3, ease: "power2.in" });
tl.from(nextElems, { x: 80, opacity: 0, duration: 0.4, ease: "power2.out" });

// 模糊切换
tl.to(currElems, { filter: "blur(15px)", opacity: 0, duration: 0.3 });
tl.from(nextElems, { filter: "blur(15px)", opacity: 0, duration: 0.4 });
```

---

## 视频生成流水线

**全自动执行，不需要中途等用户确认。** 参数补全后一路到底。

每次用户调用时，检查以下参数是否齐全。缺什么就用 `AskUserQuestion` 提问：

| 参数 | 来源优先级 | 缺失时 |
|------|----------|--------|
| 时长 | 用户说了 > `.config.json` > 自动判断 | 不追问，自动判断 |
| 视觉风格 | 用户说了 > `.config.json` 默认 | **必须问**，根据题材推荐 3-4 个方向 |
| 视频比例 | 用户说了 > 默认 1920×1080 | **必须问**，横屏/竖屏 |
| BGM | 用户说了 > `.config.json` | 不追问，按配置 |
| TTS | 用户说了 > `.config.json` | 不追问，按配置 |

**文案方向不做固定模板**。每次根据具体题材，自己想 3-4 个差异化的文案方向，用 `AskUserQuestion` 让用户选。

方向设计原则：
- 每个方向有不同的情感基调（如：热血/温情/幽默/专业）
- 每个方向标注适用场景和示例 slogan
- 不要用"一句话暴力/痛点轰炸/颠覆认知"这种通用分类，要根据当前主题定制
- 2-4 个方向即可，宁缺毋滥

示例——给游戏题材想的方向：
```
1. 情怀史诗 — "三部曲，一场战争，一个传奇"（适合系列作品）
2. 新人劝诱 — "FPS 最好的单人战役，你还没玩？"（适合拉新）
3. 角色驱动 — "记住这些名字——Price、Soap、Ghost"（适合角色丰富的作品）
4. 电影级体验 — "不只是一款游戏，是你能亲手操作的战争电影"（适合画面党）
```

示例——给 SaaS 工具想的方向：
```
1. 效率革命 — "别再手动 XXX 了，你的时间更值钱"
2. 数据说话 — "XX 万用户已经做出了选择"
3. 老板视角 — "你的团队值得更好的工具"
```

### Phase 0: 参数确认

汇总所有参数，输出确认信息后开始分析。

### Phase 1: 分析

深度理解主题，找到最打动人的角度。

**时长判断**（优先级从高到低）：
1. 用户调用时指定了秒数 → 用指定的
2. `.config.json` 有预设 → 用预设
3. 都没有 → 自动判断：

| 题材 | 建议时长 |
|------|---------|
| 单个工具/产品介绍 | 30-45s |
| 教程/操作指南 | 45-60s |
| 概念/趋势解读 | 20-30s |
| 多工具对比/合集 | 60-90s |
| 品牌/团队宣传 | 15-25s |

**网站/Web 产品**：必须用 kimi-webbridge 实地访问，截图、了解实际数据。

**开源仓库**：读取 README、下载官方截图/logo、提取真实数据。

**输出**：`分析报告.md`（一句话定位、核心卖点、目标受众、数据、素材清单）。

### Phase 2: 脚本

根据 Phase 1 确定的时长编写完整脚本。

**脚本格式**：
```markdown
# 视频脚本：<主题名>
## 时长：XXs | 风格：XXX | 视觉：XXX

| # | 时间 | 布局 | 画面描述 | 画面文字 | 台词(TTS) | 动画 |
|---|------|------|---------|---------|----------|------|
| 1 | 0-3s | A-砸脸 | 深色底+轮廓字纹理，标题居中偏上 | "XXX" | "完整口播" | 逐字弹入 |
| 2 | ... | B-左图右文 | ... | ... | ... | ... |
```

**脚本原则**：
- 每屏 ≤15 字，动词开头，口语化
- 每个场景标注使用的布局模板（A/B/C/D/E）
- 至少 2 个场景使用装饰元素（轮廓字/网格/几何线/渐变边框）
- 至少 1 个场景用非淡入淡出的过渡（滑动/缩放穿越/模糊切换）
- 第一屏必须让人停下来，最后一屏必须让人记住地址

**脚本完成后直接进入 Phase 3。**

### Phase 3: 设计

**设计稿内容**（`设计稿.md`）：

```markdown
# 设计稿：<主题名>

## 色彩
底色/主色/辅色/标签/文字/orb

## 字体层级
H0/H1/H2/H3/CTA 的字号字重用例

## 每个场景的设计说明
### 场景 1 — A-砸脸
- 底色纯色 + 左上角 200px 轮廓字作背景纹理
- 主标题 120px/900，居中偏上 60px
- 底部 2 条对角线装饰，opacity 0.2
- 标签在主标题上方 40px

### 场景 2 — B-左图右文
- 左栏 580px 截图，渐变边框 + 暗角
- 右栏 3 个玻璃态 chip，渐变文字
- 背景：细线网格 + 右上角虚线圈
```

### Phase 4: 实现

写 HTML + CSS + GSAP。

**实现检查清单**（渲染前逐项确认，不通过不渲染）：

- [ ] **每场景都有图**：至少 80% 的场景包含 `<img>` 标签或 CSS background-image。纯文字场景最多 1 个（仅限砸脸开场）
- [ ] 图片作为场景背景（全屏 `object-fit: cover` + 暗色蒙层），或作为内容卡片（带边框/阴影）
- [ ] 至少 2 个场景有几何/发光/网格装饰
- [ ] 文字设计有变化（不是全居中同字号）
- [ ] CTA 按钮有发光或边框效果
- [ ] 每屏 ≤15 字，字号 ≥28px

**图片收集**（优先用 kimi-webbridge 浏览器搜图）：

```bash
# 1. 确认 kimi-webbridge 运行
~/.kimi-webbridge/bin/kimi-webbridge status

# 2. 浏览器搜索图片（Google Images 或壁纸站）
curl -s -X POST http://127.0.0.1:10086/command \
  -d '{"action":"navigate","args":{"url":"https://www.google.com/search?q=<关键词>+wallpaper+1920x1080&tbm=isch","newTab":true},"session":"img-search"}'

# 3. 截图看搜索结果，逐个打开好的图片
# 4. 用 evaluate 提取图片 src，curl 下载到素材/
# 5. 或直接去 Steam 商店页拿官方封面和截图
```

**如果 kimi-webbridge 不可用**：
- Steam 游戏：`https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/<appid>/header.jpg`
- GitHub 仓库：`https://opengraph.githubassets.com/1/<owner>/<repo>`
- 官网截图：`curl` 下载 favicon/logo
- 通用备选：Google Images 直接 curl 搜索页源码提取图片 URL

**超时提醒**：实现阶段如果超过 15 分钟仍未开始渲染，先输出当前 HTML 让用户看，确认后再渲染。

**渲染**：
```bash
export PATH="/d/software/nvm/v22.21.1:$PATH"
cd "D:/视频生成/<project>/" && npm run check && npm run render
```
渲染完复制 MP4 到项目根目录命名为 `rendered.mp4`。

---

## 视觉风格参数速查

| 风格 | 底色 | 标题渐变 | 标签底+字 | CTA |
|------|------|---------|----------|-----|
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

## 通用规则

- 不展示安装命令，只展示能干嘛
- 标题 ≥80px，副标题 ≥36px，正文 ≥28px
- 每屏 ≤15 字，一屏一个信息
- 优先用真实截图，纯文字是最后手段
- 最后必须放链接/地址
- 每个场景 ≥2 种装饰元素

## 环境要求

- Node.js ≥ 22 (`nvm use 22`)
- FFmpeg (`scoop install ffmpeg`)
- kimi-webbridge（网站调研用）
- HyperFrames（`npx hyperframes init` 自动下载）

## 实现注意

- 符合 HyperFrames 规范：`class="clip"`、`data-start/duration/track-index`
- GSAP timeline `paused: true`，注册到 `window.__timelines`
- orb 用不同 track-index，每场景结束加 `tl.set()` hard kill
- BGM 复制到项目内 `src="bgm.mp3"`
- 不使用 `Math.random()` 或 `Date.now()`
