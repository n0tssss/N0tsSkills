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
7. 测试：`python3 ~/.hermes/scripts/github-daily-summary.py`

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
~/.hermes/scripts/github-daily-summary.py
```

### 定时任务
每天 22:00 执行，通过 cron job 自动发送到微信。

## 报告格式要求（用户偏好）

- **极简格式**，不要卡片边框、不要花哨排版
- **AI 点评要像人话**，不要"今天是高产的一天！主要在 X 上发力。新增了 Y 行代码"这种模板句式
- AI 点评根据分数区间随机选句式，同一天 seed 固定保证一致性
- **不要按组织/个人分组展示仓库**，只要顶部一行 top5 仓库概览
- 去掉多余分隔线，报告要紧凑
- 代码可视化条保留（🟩新增 🟥删除）

## 手动执行

```bash
python3 ~/.hermes/scripts/github-daily-summary.py
```

## 仓库过滤逻辑

脚本只统计以下仓库的活动，**自动排除**用户作为 collaborator 的他人仓库：
- 用户自己的仓库：`n0tssss/xxx`
- 用户所属组织的仓库：`shwkea/xxx`、`N0tsLabs/xxx`（自动获取）

Star 和 Fork 事件不受过滤影响，仍会统计。

## Pitfalls

1. **Classic Token vs Fine-grained Token**：必须用 Classic Token (ghp_)。Fine-grained Token (github_pat_) 认证方式不同，会导致 401。
2. **Token 被系统替换**：对话中粘贴的 token 会被替换为 `***`（3字符），必须通过 `write_file` 或 `execute_code` 写入文件。
3. **SSL 网络错误**：GitHub API 偶尔会触发 SSL EOF 错误。脚本使用 urllib3 Retry + HTTPAdapter 自动重试（3次，指数退避）。
4. **微信消息限流**：短时间内发太多消息会触发 `rate limited` (ret=-2)。等待几分钟后自动恢复。
5. **脚本超时**：检查太多仓库会导致超时。已限制为前 40 个仓库。
6. **飞书不能发交互式卡片**：Hermes 在飞书只能发纯文本/Markdown，不要用 `┌─┐│└─┘` 之类的文字卡片边框，效果很丑。用极简纯文本格式。
7. **AI 点评不要堆砌事实**：数据已经在报告上方展示了，点评只需要一句自然的总结。"今天卷到飞起，N0tsSkills 被你疯狂输出 1304 行！"✅ "今天是高产的一天！上午在 X 上活跃，下午在 Y 上活跃。主要在 X、Y 上发力。新增了 1304 行代码，真是码力全开！"❌

## 注意事项

- Token 需要有访问私有仓库的权限（如果需要监控私有仓库）
- GitHub API 有频率限制，脚本会自动处理
- 时区默认使用北京时间（UTC+8）
