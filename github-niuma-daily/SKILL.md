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

### 🤖 AI 点评（报告最前面）
- 综合评分（0-100+ 分）
- 工作强度等级（从"摸鱼牛马"到"超级牛马"）
- **时间段分析**：自动分析早上/上午/中午/下午/晚上的活跃情况
- 自动生成工作总结

### 🏢 组织支持
- **自动获取**用户所属的所有组织（通过 `/user/orgs` API）
- 区分公司项目和个人项目，分别展示
- 加入新组织后自动识别，无需改配置

### 📊 核心数据统计
- 提交次数、Push 次数
- PR 创建/合并/审查数量
- Issue 创建/关闭数量
- 收到的 Star、Fork 数量

### 💻 代码变更详情
- 总代码行数变化（+/-）
- 可视化代码变更条（🟩新增 🟥删除）
- 仓库级别统计（**不显示具体 commit 记录**，用户觉得太啰嗦）

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

- **AI 总结放最前面**，不要放最后
- **不要显示具体 commit 记录**，只显示仓库级别的统计
- AI 点评要包含**一天的时间段分析**（早上/上午/中午/下午/晚上在哪里活跃）
- 去掉多余的分隔线，报告要**紧凑**
- 仓库详情只显示：仓库名、提交次数、代码行数变化

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

## 注意事项

- Token 需要有访问私有仓库的权限（如果需要监控私有仓库）
- GitHub API 有频率限制，脚本会自动处理
- 时区默认使用北京时间（UTC+8）
