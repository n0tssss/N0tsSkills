## Pitfalls

### Token被系统自动替换
对话中粘贴的token会被Hermes自动替换为`***`（3字符），导致认证失败。
**必须**通过文件写入，不要在对话中粘贴token。

### Classic Token vs Fine-grained Token
- Classic Token (ghp_xxx) - 正确，支持repo+read:user权限
- Fine-grained Token (github_pat_xxx) - 错误，认证方式不同，会导致401

### 微信消息限流
短时间内发太多消息会触发 `rate limited` (ret=-2)。
**解决**：等待几分钟后自动恢复，或将推送改为飞书。

### 🔴 私有仓库不显示（严重）

**症状**：日报只显示部分仓库的活动，私有仓库完全缺失。

**原因**：GitHub API 端点选择错误：
| 端点 | 返回私有仓库 | 返回私有事件 |
|------|-------------|-------------|
| `/users/{username}/repos` | ❌ | - |
| `/user/repos` | ✅ | - |
| `/users/{username}/events/public` | - | ❌ |
| `/users/{username}/events` | - | ✅ |

**修复**：
```python
# ❌ 错误：不返回私有仓库
repos_url = f"{API_BASE}/users/{username}/repos"

# ✅ 正确：需要认证，能返回私有仓库
repos_url = f"{API_BASE}/user/repos"
params = {"affiliation": "owner", "sort": "updated"}

# ❌ 错误：只返回公开事件
events_url = f"{API_BASE}/users/{username}/events/public"

# ✅ 正确：返回所有事件（包括私有仓库）
events_url = f"{API_BASE}/users/{username}/events"
```

### 🔴 GitHub API 时间格式不支持时区（严重）

**症状**：提交查询返回空结果，但直接用 UTC 时间查询有数据。

**原因**：GitHub API 的 `since`/`until` 参数不支持带时区的 ISO 格式（`+08:00`），必须用 UTC（`Z`）。

**修复**：
```python
# ❌ 错误：带时区的 ISO 格式
since = datetime.combine(date, datetime.min.time()).replace(tzinfo=bj_tz)
params = {"since": since.isoformat()}  # 生成 "2026-06-17T00:00:00+08:00"

# ✅ 正确：UTC 格式
since_utc = date.strftime("%Y-%m-%dT00:00:00Z")
until_utc = (date + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
params = {"since": since_utc, "until": until_utc}
```

### 🔴 Git author name ≠ GitHub username

**症状**：用 `author=n0tssss` 过滤提交会漏掉大量提交。

**原因**：GitHub API 的 `author` 参数匹配的是 `commit.author.name`（Git 配置的作者名），不是 `author.login`（GitHub 登录名）。如果用户的 Git author name（如 "N0ts"）和 GitHub username（如 "n0tssss"）不同，会漏掉提交。

**修复**：
```python
# ❌ 错误：用 author 参数过滤
params = {"author": username}

# ✅ 正确：获取所有提交，在代码中过滤
all_commits = resp.json()
commits = [c for c in all_commits if c.get("author", {}).get("login") == username]
```

### 多脚本不同步

**症状**：修复了 `github-daily-summary.py`，但 `generate-report.py` 生成的图片数据还是旧的。

**原因**：存在两个脚本：
- `~/.hermes/skills/N0tsSkills/github-niuma-daily/scripts/github-daily-summary.py`（skill 目录）
- `~/.hermes/scripts/github-summary.py`（被 `generate-report.py` 调用）

`generate-report.py` 第 192 行调用的是 `~/.hermes/scripts/github-summary.py`，不是 skill 目录下的脚本。

**修复**：修改 skill 目录下的脚本后，必须同步到 `~/.hermes/scripts/`：
```bash
cp ~/.hermes/skills/N0tsSkills/github-niuma-daily/scripts/github-daily-summary.py \
   ~/.hermes/scripts/github-summary.py
```

### 仓库数量限制导致漏检

**症状**：有活动的仓库未被统计。

**原因**：脚本用 `all_repos[:40]` 限制检查数量，但用户的仓库（个人+组织）可能超过 40 个。

**修复**：
```python
# 只检查最近 7 天有更新的仓库
cutoff_date = date - timedelta(days=7)
recent_repos = []
for repo in all_repos:
    updated_at = repo.get("updated_at", "")
    if updated_at:
        repo_date = datetime.fromisoformat(updated_at.replace("Z", "+00:00")).date()
        if repo_date >= cutoff_date:
            recent_repos.append(repo)

# 最多检查 20 个
for repo_info in recent_repos[:20]:
    ...
```
