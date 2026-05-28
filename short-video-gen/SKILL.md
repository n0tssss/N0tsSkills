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

### 常用布局模式

```
A. 全屏图片 + 暗色蒙层 + 大字标题    — 开场/章节分隔
B. 左图右文/左文右图                  — 产品展示
C. 多列卡片（flex/grid）              — 功能罗列
D. 大数字冲击                         — 年份/规模/数据
E. 图片 + 标注气泡                    — 截图细节
F. 2×2 网格卡片                       — 场景/案例展示
G. 对比布局（左右分栏）               — 前后对比
H. 底部 caption 叠加（backdrop-filter）— 旁白/标题
```

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

如果启用 TTS：
1. 从脚本台词生成时间戳台词列表
2. 每句调用 MiMo API 生成 WAV
3. 在 HTML 中为每句添加独立 `<audio>` 标签
4. BGM 音量压到 0.06-0.08

---

## 实践经验

- **数据核实**：去官方渠道确认，不编数字
- **HyperFrames 可见性**：`data-start/duration` 管显示/隐藏，GSAP 只做动画
- **浮点精度**：duration = nextStart - currentStart - 0.02
- **必跑 check**：检查 overlap/溢出
- **素材先行**：素材不够不写 HTML，否则=幻灯片
- **块组件**：`npx hyperframes add <name>` 安装现成特效块

## 工具 & 环境

kimi-webbridge · HyperFrames · FFmpeg · 小米 MiMo TTS
Node.js ≥ 22

## HyperFrames 速查

```html
<div class="clip" data-start="0" data-duration="5" data-track-index="10">
```
- GSAP `paused:true` → `window.__timelines["main"]`
- orb 不同 track-index
- `tl.set()` hard kill
- 不用 `Math.random()` / `Date.now()`
