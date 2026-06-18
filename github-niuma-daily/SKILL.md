---
name: github-niuma-daily
description: GitHub 牛马日报 — 自动监控个人账号和所有组织的每日活动，生成详细的工作强度报告
---

# GitHub 牛马日报

自动监控 GitHub 用户当天活动，生成"牛马日报"。

## 首次使用引导

如果用户没有配置 token：

1. 引导用户访问 https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**（不要用 Fine-grained token，认证方式不同）
3. 勾选 **repo** + **read:user**
4. Expiration 选择 **90 days** 或 **No expiration**
5. 生成后立刻复制 token
6. **重要**：由于系统会自动将 token 替换为 `***`，必须通过文件写入：
   ```python
   # 用 execute_code 或 terminal 写入
   with open(os.path.expanduser("~/.hermes/.github_token"), "w") as f:
       f.write("ghp_xxxxx")
   ```
7. 测试：`python3 ~/.hermes/scripts/github-summary.py`

## 功能特性

### 🤖 AI 点评
- 综合评分（0-100+ 分）+ 工作强度等级
- **自然语言风格**，像人说话而不是堆砌事实
- 根据分数区间随机选句式（同一天 seed 固定，结果一致）
- 包含主仓库名、时段特征、PR/Star 等亮点（有才说，没有不凑）
- **不要**：逐条列举数据（数据已经在上方展示过了）

### 📊 核心数据（极简格式）
- 提交次数、Push 次数
- 代码行数变化（+/-）+ 可视化条
- PR 创建/合并、Issue 创建/关闭
- Star、Fork、活跃仓库数
- 仓库概览：按提交数排序 top5，格式 `仓库名(次数) · ...`

### ❌ 不展示
- 具体 commit 记录（太啰嗦）
- 按组织/个人分组的仓库详情（用户只要数据，不要分类展开）
- 文字卡片边框（飞书不支持交互式卡片，文字卡片很丑）

## 评分标准

| 分数 | 等级 | 描述 |
|------|------|------|
| 80+ | 🔥🔥🔥🔥 超级牛马 | 代码之神！GitHub 应该给你发工资！ |
| 50-79 | 🔥🔥🔥 顶级牛马 | 卷王本王！代码量可以绕地球一圈！ |
| 30-49 | 🔥🔥 勤劳牛马 | 高产如母猪！干了不少实事！ |
| 15-29 | 🔥 正常牛马 | 稳扎稳打，正常发挥！ |
| 8-14 | 💨 轻度牛马 | 写了一点点，也算进步... |
| 3-7 | 😴 划水牛马 | 主要在思考人生... |
| 0-2 | 🏖️ 摸鱼牛马 | 休息日？还是在憋大招？ |

## 配置

### Token 文件
```
~/.hermes/.github_token
```
存放 GitHub Personal Access Token (classic)，需要 `repo` + `read:user` 权限。

### 脚本位置
```
~/.hermes/scripts/github-summary.py
```

### 定时任务
每天 22:00 执行，通过 cron job 自动发送到微信（cron job ID: 7e78b3329620）。

## 报告格式要求（用户偏好）

- **极简格式**，不要卡片边框、不要花哨排版
- **AI 点评要像人话**，不要"今天是高产的一天！主要在 X 上发力。新增了 Y 行代码"这种模板句式
- AI 点评根据分数区间随机选句式，同一天 seed 固定保证一致性
- **不要按组织/个人分组展示仓库**，只要顶部一行 top5 仓库概览
- 去掉多余分隔线，报告要紧凑
- 代码可视化条保留（🟩新增 🟥删除）

## HTML 可视化报告（截图发送）

用户要求将日报转为**手机竖屏 HTML 页面**，截图后发送。

### 设计规范
- 布局：竖屏，max-width: 400px，padding: 24px 16px
- 风格：深色极简（#0a0a0f 底色，#12121a 卡片）
- 字体：Inter + JetBrains Mono（数字等宽）
- 状态卡片：顶部渐变条 + 评分大数字 + AI点评
- 统计：2x2 网格（提交/代码行/PR/仓库）
- 代码量：进度条可视化
- 仓库排行：TOP3 带排名徽章

### 生成流程
1. 运行 `python3 ~/.hermes/scripts/github-summary.py --date <date>` 获取文本数据
2. 用 Python 生成 HTML 文件到 `~/.hermes/media/daily-report.html`
3. 启动本地 HTTP 服务器（`python3 -m http.server 8765`）
4. 用 Kimi WebBridge 打开页面，设置手机视口，截图
5. 截图保存到 `~/.hermes/media/daily-report.png`，用 MEDIA: 发送

### 截图技巧

**⚠️ 不要用 Kimi WebBridge 截图** — 它无法调整视口大小，截出来是桌面宽度，内容挤在左边。

用 Playwright 截手机尺寸：

```bash
cd /Users/wkea/.hermes/hermes-agent && node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true
  });
  const page = await context.newPage();
  await page.goto('file:///Users/wkea/.hermes/media/daily-report.html');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/Users/wkea/.hermes/media/daily-report.png', fullPage: true });
  await browser.close();
  console.log('done');
})();
"
```

然后用 `MEDIA:/Users/wkea/.hermes/media/daily-report.png` 发送。

## 图片报告生成

除了文本报告，还支持生成精美的手机竖屏图片报告。

### 生成流程

```bash
# 1. 生成 HTML 报告
python3 ~/.hermes/skills/productivity/github-niuma-daily/scripts/generate-report.py

# 2. 截图为 PNG（手机尺寸 390x844 @2x）
node ~/.hermes/skills/productivity/github-niuma-daily/scripts/screenshot.js \
  <html_path> <output_path>
```

### 完整流程（推荐）

```bash
# 日报图片
REPORT=$(python3 ~/.hermes/skills/productivity/github-niuma-daily/scripts/generate-report.py)
HTML_PATH=$(echo $REPORT | jq -r '.html_path')
OUTPUT_PATH=~/.hermes/media/report-$(date +%Y%m%d).png
node ~/.hermes/skills/productivity/github-niuma-daily/scripts/screenshot.js "$HTML_PATH" "$OUTPUT_PATH"
echo "MEDIA:$OUTPUT_PATH"
```

### 图片报告特点

- **手机竖屏**：390x844 像素，2x 高清
- **深色主题**：暗黑背景 + 橙色主色调
- **数据可视化**：进度条、排名徽章、统计卡片
- **一键生成**：脚本自动解析文本输出并生成图片

### 模板文件

- 日报模板：`templates/daily.html`
- 周报模板：`templates/weekly.html`

## 手动执行

```bash
# 文本报告
python3 ~/.hermes/scripts/github-daily-summary.py

# 图片报告
python3 ~/.hermes/skills/N0tsSkills/github-niuma-daily/scripts/generate-report.py
```

## 仓库过滤逻辑与 repos_scope

脚本通过 `repos_scope` 参数控制统计范围：

| 模式 | repos_scope | 说明 | 用途 |
|------|-------------|------|------|
| 全部 | `"all"` | 个人仓库 + 所有组织 | **日报** |
| 仅组织 | `"orgs"` | 所有组织（不含个人仓库） | 备用 |
| 指定组织 | `["shwkea"]` | 只统计指定组织 | **周报** |

**日报 vs 周报区别**：
- 日报（cron job 22:00）：`repos_scope="all"`，统计全部
- 周报（`--week`）：`repos_scope=["shwkea"]`，只统计公司组织

**重要**：必须使用 `/user/repos` 端点（需要认证）才能获取私有仓库。`/users/{username}/repos` 不返回私有仓库。

## 用户账号信息

| 账号 | 仓库数 | 说明 |
|------|--------|------|
| n0tssss (个人) | 30 | 9 私有 + 21 公开 |
| shwkea (组织) | 23 | 公司组织 |
| N0tsLabs (组织) | 14 | 个人组织 |

日报统计范围：个人仓库 + shwkea + N0tsLabs

## 仓库显示格式

仓库名显示 `org/repo` 格式（如 `shwkea/wkea-api`），而不是只显示 `repo`，这样用户一眼能看出属于哪个组织。

Star 和 Fork 事件不受过滤影响，仍会统计。

## Pitfalls

详见 `references/pitfalls.md`，包含以下关键问题：

1. **🔴 私有仓库不显示** — 必须用 `/user/repos` 和 `/users/{username}/events`，不能用公开端点
2. **🔴 GitHub API 时间格式** — `since`/`until` 必须用 UTC 格式（`Z`），不支持带时区的 ISO 格式
3. **🔴 Git author name ≠ GitHub username** — 不能用 `author` 参数过滤，要在代码中按 `login` 过滤
4. **🔴 多脚本不同步** — 修改 skill 目录脚本后必须同步到 `~/.hermes/scripts/`，否则 generate-report.py 用旧版
5. **Classic Token vs Fine-grained Token** — 必须用 Classic Token (ghp_)
6. **Token 被系统替换** — 必须通过文件写入
7. **脚本超时** — 只检查最近 7 天更新的仓库，最多 20 个
8. **Cron Job no_agent 陷阱** — `no_agent: true` 会忽略 prompt
9. **飞书不能发交互式卡片** — 用极简纯文本格式
10. **AI 点评不要堆砌事实** — 数据已在报告展示，点评只需一句总结

## 注意事项

- Token 需要有访问私有仓库的权限（如果需要监控私有仓库）
- GitHub API 有频率限制，脚本会自动处理
- 时区默认使用北京时间（UTC+8）
