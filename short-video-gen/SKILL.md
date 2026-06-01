---
name: short-video-gen
description: 视频制作 — 选题评估→参数确认→信息收集→脚本设计→实现渲染，全流程带审核关卡
argument-hint: "<视频主题描述>"
level: 4
---

# 视频制作

用户提想法 → AI 走完整流程 → 输出视频。

---

## 架构设计

**AI负责决策和审核** → 输出结构化JSON
**脚本负责执行** → 根据JSON生成HyperFrames代码、TTS对轨等

```
用户提想法
    │
    ▼
Stage 0  选题评估   竞品调研 + 卖点分析 + 流量预估 + 用户确认
    │
    ▼
Stage 1  参数确认   用 AskUserQuestion 逐一确认视频规格，汇总打印
    │
    ▼
Stage 2  信息收集   深度调研 + 素材收集 + 数据核实
    │
    ▼
Gate 2   素材审核   6 项检查，不通过打回 Stage 2（标注缺什么）
    │
    ▼
Stage 3  脚本设计   分镜表 + 每场景素材/文字/动画/时长
    │
    ▼
Stage 3.5 动画设计   每个场景的入场/强调/退场动画 + 视觉风格
    │
    ▼
Stage 3.6 对轨设计   生成TTS → 计算时长 → 调整场景时间轴
    │
    ▼
Gate 3   方案审核   5 项检查 + 对轨审核，不通过打回 Stage 3（标注改哪里）
    │
    ▼
Stage 4  输出JSON   结构化视频数据（scenes/animations/audio）
    │
    ▼
Stage 5  代码生成   脚本根据JSON生成HyperFrames HTML
    │
    ▼
Stage 6  渲染输出   hyperframes render → MP4
    │
    ▼
Gate 4   最终审核   技术 + 内容，不通过回对应阶段
    │
    ▼
rendered.mp4
```

---

## Stage 0: 选题评估

用户提出想法后，先分析值不值得做。

### 0.1 竞品调研

Web 搜索同类内容，收集真实数据：

```
搜 B站：site:bilibili.com <关键词>
搜抖音：site:douyin.com <关键词>
搜 YouTube：site:youtube.com <关键词>
```

提取：同类最高播放量、常见角度、优缺点、评论区观众的未满足需求。

### 0.2 选题分析

- **一句话卖点**：看完能获得什么？
- **目标受众**：谁看？什么场景看？
- **差异化**：和同类内容有什么不同？
- **流量潜力**：有人搜这个话题吗？适合传播吗？
- **执行可行性**：素材能收集到吗？

### 0.3 用户确认

用 `AskUserQuestion` 确认方向：

```
"我的分析：[简述卖点+受众+差异化]。这个方向可以吗？"
选项：[1] 可以，继续 [2] 换个角度 [3] 我再想想
```

---

## Stage 1: 参数确认

用 `AskUserQuestion` 逐一确认。用户说"你定"就跳过该项。

```
时长：[1] AI 判断 [2] 15s [3] 30s [4] 60s [5] 自定义

视觉风格：
  [1] AI 推荐 [2] 赛博朋克 [3] 极简白 [4] 暗金 [5] 活力橙蓝
  [6] 暗夜绿 [7] 霓虹粉紫 [8] 纯黑暴力 [9] 暖橘日落 [10] 冰川蓝

视频比例：[1] 1920×1080 [2] 1080×1920 [3] 其他

BGM：[1] 自动合成 [2] 不加 [3] 手动提供
TTS：[1] 不加 [2] 小米 MiMo（需 API Key）
```

确认完毕后，打印汇总让用户过目。

---

## Stage 2: 信息收集

**不全不进 Stage 3。**

### 按类型调研

**网站/产品/服务**（kimi-webbridge）：
- 首页、关于、功能、定价、联系——逐个页面截图
- 提取真实数据（用户数、年份、规模、slogan）
- 下载 logo，记录可用文案
- 有 Demo 的打开截图

**开源项目**：
- 读 README 提取功能、技术栈、使用场景
- 下载官方截图/Logo（GitHub `assets/` 目录）
- 获取真实数据（Stars/Forks/License）
- 有官网的去截图

**游戏/影视/文化**：
- kimi-webbridge 搜 Google Images/壁纸站，下载官方海报、角色图、场景截图
- Web 搜索收集评分、获奖、名场面、经典台词
- ≥5 张不同内容的高清图

**教程/操作指南**：
- kimi-webbridge 实际操作流程，每步截图

### 数据核实

所有引用数字必须有来源。不确定的宁可不用，不可瞎编。

---

### Gate 2: 素材审核

不通过时标注具体缺什么，打回 Stage 2：

```
□ 素材数量：≥5 个不同文件？
  → 缺：______
□ 素材多样性：不同页面/角度/内容？（不是同一张图反复用）
  → 缺：______
□ 有高清主视觉图吗？（能全屏铺满的）
□ 有 logo 吗？
□ 关键数据有来源吗？（不是编的）
  → 可疑项：______
□ 现有素材能覆盖每个场景吗？（N 个场景需要 N 张不同的图）
```

---

## Stage 3: 脚本设计

产出分镜表，每行一个场景：

| # | 时间 | 素材 | 画面描述 | 文字 | 动画 |
|---|------|------|---------|------|------|
| 1 | 0-4s | hero.jpg | 全屏蒙层+大字 | "XXX" | 模糊 reveal |
| 2 | ... | ... | ... | ... | ... |

要求：
- 前 3 秒有钩子（反常识/数字冲击/痛点/好奇）
- 每场景用不同素材图
- 相邻场景布局不重复
- 每屏文字简短有力

---

## Stage 3.5: 动画设计

为每个场景设计具体的动画效果：

### 动画类型库

**入场动画**：
- `fadeIn` - 淡入
- `slideInLeft` - 从左滑入
- `slideInRight` - 从右滑入
- `slideInUp` - 从下滑入
- `scaleIn` - 缩放进入
- `blurIn` - 模糊进入
- `typewriter` - 打字机效果

**强调动画**：
- `pulse` - 脉冲缩放
- `shake` - 抖动
- `glow` - 发光
- `bounce` - 弹跳

**退场动画**：
- `fadeOut` - 淡出
- `slideOutLeft` - 向左滑出
- `slideOutRight` - 向右滑出
- `scaleOut` - 缩放退出
- `blurOut` - 模糊退出

### 设计输出格式

```
场景1：
- 入场：文字从下方 slideInUp，持续0.5s
- 强调：标题 pulse 缩放1.2倍，持续0.3s
- 退场：整体 fadeOut，持续0.3s

场景2：
- 入场：背景从左向右滑入
- 强调：关键词 glow 发光
- 退场：整体 blurOut
```

---

## Stage 3.6: 对轨设计

**TTS和视频必须同步。**

### 流程

1. **生成TTS音频**
   - 把所有旁白文本写入 `tts-input.txt`
   - 调用小米MiMo TTS生成音频
   - 保存为 `voiceover.wav`

2. **计算每句话时长**
   - 分割音频为单独的句子
   - 计算每句的开始时间和结束时间
   - 输出 `timing.json`

3. **调整场景时间轴**
   - 每个场景的 `data-start` 和 `data-duration` 必须匹配语音
   - 如果语音比场景长，延长场景
   - 如果语音比场景短，缩短场景或添加停顿

4. **生成时间轴JSON**
   ```json
   {
     "scenes": [
       {
         "id": "scene-1",
         "text": "每天重复的事",
         "start": 0,
         "duration": 2.5,
         "voiceStart": 0,
         "voiceEnd": 2.5
       }
     ]
   }
   ```

### 注意事项

- 场景切换要在句子结束前0.2秒开始，避免突兀
- 相邻场景有0.1秒重叠，实现平滑过渡
- 如果场景没有配音，设置固定时长（建议3-4秒）

---

## Gate 3: 方案审核

不通过标注改哪里，打回 Stage 3：

```
□ 一句话能说清这个视频讲什么吗？
  → 说不清说明：______
□ 前 3 秒够强吗？
□ 每个场景都指定了素材吗？
□ 场景布局有变化吗（≥3 种）？
□ 符合 Stage 0-1 确认的方向和参数吗？

【新增】对轨审核：
□ TTS音频时长和场景时长匹配吗？
□ 每句话的开始/结束时间和场景切换对得上吗？
□ 有没有语音还没说完就切场景的情况？
□ 有没有场景等太久才开始说话的情况？
```

---

## Stage 4: 输出JSON

AI决策完成后，输出结构化JSON：

```json
{
  "project": {
    "name": "hermes-intro",
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "duration": 40
  },
  "style": {
    "theme": "cyberpunk",
    "colors": {
      "primary": "#00d4ff",
      "secondary": "#1a1a2e",
      "accent": "#ff4444",
      "background": "#0a0a0a"
    },
    "font": {
      "main": "system-ui",
      "size": {
        "title": 72,
        "subtitle": 48,
        "caption": 36
      }
    }
  },
  "scenes": [
    {
      "id": "scene-1",
      "name": "痛点引入",
      "start": 0,
      "duration": 4,
      "background": "linear-gradient(135deg, #1a1a2e, #16213e)",
      "elements": [
        {
          "type": "text",
          "id": "title-1",
          "content": "每天重复的事",
          "position": { "x": "center", "y": "center" },
          "style": {
            "fontSize": 72,
            "fontWeight": "bold",
            "color": "white",
            "textAlign": "center"
          },
          "animation": {
            "enter": { "type": "scaleIn", "duration": 0.5 },
            "exit": { "type": "fadeOut", "duration": 0.3 }
          }
        }
      ]
    }
  ],
  "audio": {
    "enabled": false,
    "tts": {
      "provider": "xiaomi-mimo",
      "voice": "Chloe",
      "text": "每天重复的事...",
      "segments": []
    }
  }
}
```

---

## Stage 5: 代码生成

脚本根据JSON生成HyperFrames HTML代码：

```bash
python3 ~/.hermes/skills/N0tsSkills/short-video-gen/scripts/generate.py video-spec.json
```

脚本自动处理：
- HTML结构生成
- CSS样式注入
- GSAP动画配置
- HyperFrames时间轴注册
- 音频元素（如果有）

---

## Stage 6: 渲染输出

```bash
cd <project-dir>
hyperframes render --output rendered.mp4
```

---

## Stage 7: 最终审核

播放视频，检查：

```
□ 视频能正常播放？无卡帧/花屏/黑屏？
□ 内容符合 Stage 3 的设计方案？
□ 动画效果流畅吗？
□ 作为观众，觉得这视频好看吗？
  → 不好看的原因：______
```

---

## 工具 & 环境

kimi-webbridge · HyperFrames · FFmpeg · 小米 MiMo TTS
Node.js ≥ 22 · FFmpeg · Python 3.x

## 参考文件

- `references/hyperframes-pitfalls.md` - HyperFrames常见错误及修复
- `references/gsap-patterns.md` - GSAP动画模式库
- `templates/video-spec-template.json` - 视频配置JSON模板
- `scripts/generate.py` - 根据JSON生成HyperFrames HTML的脚本

---

## HyperFrames 速查

```html
<div class="clip" data-start="0" data-duration="5.0" data-track-index="10">
```
- GSAP `paused:true` → `window.__timelines["main"]`
- orb 不同 track-index 避免 overlap
- `tl.set()` hard kill，不用 `Math.random()`/`Date.now()`

---

## 常见问题

### TTS和视频不同步
- **原因**：没有对轨，直接用固定时长
- **解决**：Stage 3.6 必须计算每句话时长，调整场景时间轴

### 动画效果差
- **原因**：只用了简单的opacity渐显渐隐
- **解决**：Stage 3.5 必须设计具体动画效果（缩放、位移、模糊等）

### HyperFrames渲染失败
- **原因**：HTML模板不符合要求
- **解决**：用脚本生成，不要手写HTML

---

## Pitfalls（踩坑记录）

### HyperFrames HTML必须包含的属性
- `data-composition-id` - 必须在根元素上
- `data-width` 和 `data-height` - 必须在根元素上
- `data-start="0"` - 必须在根元素上
- `window.__timelines[compositionId]` - 必须注册timeline
- `window.__hf = { duration, seek }` - 必须暴露给HyperFrames

### GSAP动画限制
- **禁止 `repeat: -1`**（无限循环）：HyperFrames无法处理，会报错
- 有限次数用 `repeat: Math.floor(duration / cycleDuration) - 1`
- 选择器必须用字符串形式 `'#element-id'`，不能用私有字段语法

### 动画代码生成模式
```javascript
// 正确：用tl.add()添加动画到timeline
tl.add(() => { gsap.fromTo('#title', {opacity: 0}, {opacity: 1, duration: 0.5}) }, startTime);

// 错误：直接在timeline方法中使用复杂动画
tl.to('#title', { /* 动画参数 */ });  // 这样会导致时序问题
```

### 常见渲染错误及修复
1. **`window.__hf not ready`** - 检查是否正确暴露了window.__hf
2. **`Private field must be declared`** - 选择器用了#id语法但没加引号
3. **`gsap_infinite_repeat`** - 把repeat: -1改为有限次数
4. **`root_missing_dimensions`** - 根元素缺少data-width/data-height
5. **`missing_timeline_registry`** - 忘记注册window.__timelines

### 视频效果差的根因
- ❌ 只用opacity渐显渐隐 = 幻灯片效果
- ✅ 必须组合使用：缩放(scale) + 位移(translate) + 模糊(blur) + 发光(glow)
- ✅ 每个场景至少3种动画：入场、强调、退场
- ✅ 相邻场景用不同动画类型，避免重复

### AI决策 → 代码生成的架构
- AI只负责：选题、脚本、动画设计、审核
- 脚本负责：HTML生成、动画代码、时间轴计算
- 不要让AI直接写HTML/CSS/JS代码，容易出错
