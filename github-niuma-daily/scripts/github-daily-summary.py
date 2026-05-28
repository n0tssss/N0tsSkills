#!/usr/bin/env python3
"""
GitHub 每日活动强度总结 v5
自动获取所有组织，监控个人和所有组织的活动
AI 总结放前面，去掉具体 commit，增加时间段点评
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置
TOKEN_FILE = os.path.expanduser("~/.hermes/.github_token")
GITHUB_USERNAME = "n0tssss"
API_BASE = "https://api.github.com"


def get_token():
    """从文件读取 token"""
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ 错误：Token 文件不存在: {TOKEN_FILE}", file=sys.stderr)
        sys.exit(1)
    
    with open(TOKEN_FILE, "r") as f:
        token = f.read().strip()
    
    if not token or len(token) < 10:
        print(f"❌ 错误：Token 无效或为空", file=sys.stderr)
        sys.exit(1)
    
    return token


def get_headers():
    """获取 API 请求头"""
    token = get_token()
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Hermes-Agent"
    }


def get_session():
    """获取带有重试机制的 requests session"""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_user_orgs():
    """获取用户所属的所有组织"""
    url = f"{API_BASE}/user/orgs"
    headers = get_headers()
    session = get_session()
    resp = session.get(url, headers=headers, params={"per_page": 100})
    
    if resp.status_code == 200:
        return [org["login"] for org in resp.json()]
    return []


def fetch_user_events(username, date):
    """获取用户今日的公开事件"""
    url = f"{API_BASE}/users/{username}/events/public"
    events = []
    page = 1
    headers = get_headers()
    
    while True:
        session = get_session()
        resp = session.get(url, headers=headers, params={"page": page, "per_page": 100})
        if resp.status_code != 200:
            break
        
        data = resp.json()
        if not data:
            break
        
        for event in data:
            event_date = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            bj_tz = timezone(timedelta(hours=8))
            event_date_bj = event_date.astimezone(bj_tz)
            
            if event_date_bj.date() < date:
                return events
            
            if event_date_bj.date() == date:
                events.append(event)
        
        page += 1
        if page > 10:
            break
    
    return events


def fetch_org_events(org_name, date):
    """获取组织今日的事件"""
    url = f"{API_BASE}/orgs/{org_name}/events"
    events = []
    page = 1
    headers = get_headers()
    
    while True:
        session = get_session()
        resp = session.get(url, headers=headers, params={"page": page, "per_page": 100})
        if resp.status_code != 200:
            break
        
        data = resp.json()
        if not data:
            break
        
        for event in data:
            event_date = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00"))
            bj_tz = timezone(timedelta(hours=8))
            event_date_bj = event_date.astimezone(bj_tz)
            
            if event_date_bj.date() < date:
                return events
            
            if event_date_bj.date() == date:
                actor = event.get("actor", {})
                if actor.get("login") == GITHUB_USERNAME:
                    events.append(event)
        
        page += 1
        if page > 10:
            break
    
    return events


def fetch_repo_commits(username, org_names, date):
    """获取各仓库的详细提交信息"""
    headers = get_headers()
    session = get_session()
    repo_commits = {}
    bj_tz = timezone(timedelta(hours=8))
    since = datetime.combine(date, datetime.min.time()).replace(tzinfo=bj_tz)
    until = since + timedelta(days=1)
    
    repos_url = f"{API_BASE}/users/{username}/repos"
    resp = requests.get(repos_url, headers=headers, params={"per_page": 100, "sort": "updated"})
    user_repos = resp.json() if resp.status_code == 200 else []
    
    all_repos = []
    for repo in user_repos:
        all_repos.append({"name": repo["name"], "owner": username, "source": "personal"})
    
    for org_name in org_names:
        org_repos_url = f"{API_BASE}/orgs/{org_name}/repos"
        resp = requests.get(org_repos_url, headers=headers, params={"per_page": 100, "sort": "updated"})
        if resp.status_code == 200:
            for repo in resp.json():
                all_repos.append({"name": repo["name"], "owner": org_name, "source": "org"})
    
    for repo_info in all_repos[:40]:
        repo_name = repo_info["name"]
        owner = repo_info["owner"]
        
        commits_url = f"{API_BASE}/repos/{owner}/{repo_name}/commits"
        resp = session.get(commits_url, headers=headers, params={
            "since": since.isoformat(),
            "until": until.isoformat(),
            "author": username,
            "per_page": 100
        })
        
        if resp.status_code == 200:
            commits = resp.json()
            if commits:
                commit_times = []
                total_additions = 0
                total_deletions = 0
                
                for commit in commits:
                    commit_url = commit["url"]
                    commit_resp = session.get(commit_url, headers=headers)
                    
                    if commit_resp.status_code == 200:
                        commit_data = commit_resp.json()
                        stats = commit_data.get("stats", {})
                        commit_time = datetime.fromisoformat(
                            commit_data["commit"]["author"]["date"].replace("Z", "+00:00")
                        ).astimezone(bj_tz)
                        
                        commit_times.append(commit_time.strftime("%H:%M"))
                        total_additions += stats.get("additions", 0)
                        total_deletions += stats.get("deletions", 0)
                
                repo_key = f"{owner}/{repo_name}"
                repo_commits[repo_key] = {
                    "count": len(commits),
                    "additions": total_additions,
                    "deletions": total_deletions,
                    "times": commit_times,
                    "source": repo_info["source"],
                    "org": owner if repo_info["source"] == "org" else None
                }
    
    return repo_commits


def analyze_events(events, username, org_names):
    """分析事件，统计活动（只统计用户自己的仓库和所属组织的仓库）"""
    allowed_prefixes = [f"{username}/"] + [f"{org}/" for org in org_names]
    
    stats = {
        "commits": 0,
        "push_events": 0,
        "pr_created": 0,
        "pr_merged": 0,
        "pr_reviewed": 0,
        "issues_created": 0,
        "issues_closed": 0,
        "issue_comments": 0,
        "stars": 0,
        "forks": 0,
        "repos_active": set(),
        "timeline": []
    }
    
    bj_tz = timezone(timedelta(hours=8))
    
    for event in events:
        event_type = event["type"]
        repo_name = event["repo"]["name"]
        payload = event["payload"]
        event_time = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00")).astimezone(bj_tz)
        
        # 只统计用户自己的仓库和所属组织的仓库
        is_allowed = any(repo_name.startswith(prefix) for prefix in allowed_prefixes)
        if not is_allowed:
            # 但是 star 和 fork 事件还是统计
            if event_type == "WatchEvent" and payload.get("action") == "started":
                stats["stars"] += 1
            elif event_type == "ForkEvent":
                stats["forks"] += 1
            continue
        
        stats["repos_active"].add(repo_name)
        
        timeline_entry = {
            "time": event_time.strftime("%H:%M"),
            "repo": repo_name
        }
        
        if event_type == "PushEvent":
            stats["push_events"] += 1
            commit_count = len(payload.get("commits", []))
            stats["commits"] += commit_count
            timeline_entry["action"] = f"推送了 {commit_count} 个提交"
            
        elif event_type == "PullRequestEvent":
            action = payload.get("action")
            pr = payload.get("pull_request", {})
            if action == "opened":
                stats["pr_created"] += 1
                timeline_entry["action"] = f"创建了 PR: {pr.get('title', '')[:40]}"
            if pr.get("merged"):
                stats["pr_merged"] += 1
                timeline_entry["action"] = f"合并了 PR: {pr.get('title', '')[:40]}"
                
        elif event_type == "PullRequestReviewEvent":
            stats["pr_reviewed"] += 1
            timeline_entry["action"] = "审查了 PR"
            
        elif event_type == "IssuesEvent":
            action = payload.get("action")
            issue = payload.get("issue", {})
            if action == "opened":
                stats["issues_created"] += 1
                timeline_entry["action"] = f"创建了 Issue: {issue.get('title', '')[:40]}"
            elif action == "closed":
                stats["issues_closed"] += 1
                timeline_entry["action"] = f"关闭了 Issue: {issue.get('title', '')[:40]}"
                
        elif event_type == "IssueCommentEvent":
            stats["issue_comments"] += 1
            timeline_entry["action"] = "评论了 Issue"
            
        elif event_type == "WatchEvent":
            if payload.get("action") == "started":
                stats["stars"] += 1
                timeline_entry["action"] = "收藏了仓库"
                
        elif event_type == "ForkEvent":
            stats["forks"] += 1
            timeline_entry["action"] = "Fork 了仓库"
        
        if "action" in timeline_entry:
            stats["timeline"].append(timeline_entry)
    
    return stats


def calculate_score(commits, prs, issues, additions, deletions):
    """计算综合评分"""
    base_score = commits * 2 + prs * 5 + issues * 3
    code_score = min((additions + deletions) / 100, 20)
    total = base_score + code_score
    return int(total)


def get_strength_level(score):
    """根据评分获取强度等级"""
    if score >= 80:
        return "🔥🔥🔥🔥 超级牛马", "今天你是代码之神！GitHub 应该给你发工资！"
    elif score >= 50:
        return "🔥🔥🔥 顶级牛马", "卷王本王！今天的代码量可以绕地球一圈！"
    elif score >= 30:
        return "🔥🔥 勤劳牛马", "高产如母猪！今天干了不少实事！"
    elif score >= 15:
        return "🔥 正常牛马", "稳扎稳打，正常发挥，没有摸鱼！"
    elif score >= 8:
        return "💨 轻度牛马", "写了一点点，也算进步吧..."
    elif score >= 3:
        return "😴 划水牛马", "今天主要在思考人生，偶尔写两行代码。"
    else:
        return "🏖️ 摸鱼牛马", "今天是休息日？还是在憋大招？"


def format_code_bar(additions, deletions, max_width=20):
    """生成代码变更的可视化条"""
    total = additions + deletions
    if total == 0:
        return "▱▱▱▱▱▱▱▱▱▱"
    
    add_width = int((additions / total) * max_width)
    del_width = max_width - add_width
    
    return "🟩" * add_width + "🟥" * del_width


def analyze_time_periods(timeline, repo_commits):
    """分析一天中不同时段的工作情况"""
    if not timeline:
        return "今天没有活动记录。"
    
    # 按时段分组
    periods = {
        "早上(6-9点)": [],
        "上午(9-12点)": [],
        "中午(12-14点)": [],
        "下午(14-18点)": [],
        "晚上(18-22点)": [],
        "深夜(22-6点)": []
    }
    
    for entry in timeline:
        hour = int(entry["time"].split(":")[0])
        if 6 <= hour < 9:
            periods["早上(6-9点)"].append(entry)
        elif 9 <= hour < 12:
            periods["上午(9-12点)"].append(entry)
        elif 12 <= hour < 14:
            periods["中午(12-14点)"].append(entry)
        elif 14 <= hour < 18:
            periods["下午(14-18点)"].append(entry)
        elif 18 <= hour < 22:
            periods["晚上(18-22点)"].append(entry)
        else:
            periods["深夜(22-6点)"].append(entry)
    
    # 找出活跃时段
    active_periods = []
    for period_name, entries in periods.items():
        if entries:
            repos = set(e["repo"].split("/")[-1] for e in entries)
            active_periods.append(f"{period_name}在{'、'.join(repos)}上活跃")
    
    if not active_periods:
        return "今天没有活动记录。"
    
    return "，".join(active_periods) + "。"


def generate_ai_summary(stats, repo_commits, score, timeline):
    """生成 AI 风格的总结，包含时间段点评"""
    total_additions = sum(r["additions"] for r in repo_commits.values())
    total_deletions = sum(r["deletions"] for r in repo_commits.values())
    total_commits = sum(r["count"] for r in repo_commits.values())
    
    personal_repos = [k for k, v in repo_commits.items() if v["source"] == "personal"]
    org_repos = [k for k, v in repo_commits.items() if v["source"] == "org"]
    
    org_groups = defaultdict(list)
    for k, v in repo_commits.items():
        if v["source"] == "org" and v["org"]:
            org_groups[v["org"]].append(k)
    
    main_repos = sorted(repo_commits.items(), key=lambda x: x[1]["count"], reverse=True)[:3]
    
    summary_parts = []
    
    # 总体评价
    if score >= 50:
        summary_parts.append("今天是高产的一天！")
    elif score >= 20:
        summary_parts.append("今天工作状态不错！")
    elif score >= 10:
        summary_parts.append("今天算是正常发挥。")
    else:
        summary_parts.append("今天比较轻松~")
    
    # 时间段分析
    time_analysis = analyze_time_periods(timeline, repo_commits)
    summary_parts.append(time_analysis)
    
    # 主要工作
    if main_repos:
        repo_names = "、".join([r[0].split("/")[-1] for r in main_repos])
        summary_parts.append(f"主要在 {repo_names} 上发力。")
    
    # 组织 vs 个人
    if org_groups:
        org_info = []
        for org, repos in org_groups.items():
            org_info.append(f"{org} ({len(repos)} 个仓库)")
        summary_parts.append(f"公司/组织项目：{'、'.join(org_info)}。")
    
    if personal_repos:
        summary_parts.append(f"个人项目 {len(personal_repos)} 个仓库活跃。")
    
    # 代码量
    if total_additions > 1000:
        summary_parts.append(f"新增了 {total_additions} 行代码，真是码力全开！")
    elif total_additions > 500:
        summary_parts.append(f"写了 {total_additions} 行新代码，效率不错。")
    elif total_additions > 0:
        summary_parts.append(f"新增 {total_additions} 行代码。")
    
    # 提交数
    if total_commits >= 20:
        summary_parts.append(f"{total_commits} 次提交，堪称提交狂魔！")
    elif total_commits >= 10:
        summary_parts.append(f"{total_commits} 次提交，节奏很稳。")
    
    # PR 和 Issues
    if stats["pr_created"] > 0 or stats["pr_merged"] > 0:
        summary_parts.append(f"处理了 {stats['pr_created']} 个 PR 创建、{stats['pr_merged']} 个合并。")
    
    if stats["issues_created"] > 0 or stats["issues_closed"] > 0:
        summary_parts.append(f"Issue 方面：新建 {stats['issues_created']} 个、关闭 {stats['issues_closed']} 个。")
    
    if stats["stars"] > 0:
        summary_parts.append(f"还收到了 {stats['stars']} 个 Star，有人认可你的工作！")
    
    return " ".join(summary_parts)


def generate_report(stats, repo_commits, username, date):
    """生成完整的日报"""
    total_additions = sum(r["additions"] for r in repo_commits.values())
    total_deletions = sum(r["deletions"] for r in repo_commits.values())
    total_commits = sum(r["count"] for r in repo_commits.values())
    
    score = calculate_score(
        total_commits,
        stats["pr_created"] + stats["pr_merged"],
        stats["issues_created"],
        total_additions,
        total_deletions
    )
    
    strength, comment = get_strength_level(score)
    date_str = date.strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
    code_bar = format_code_bar(total_additions, total_deletions)
    ai_summary = generate_ai_summary(stats, repo_commits, score, stats["timeline"])
    
    # 区分个人和各组织仓库
    personal_repos = {k: v for k, v in repo_commits.items() if v["source"] == "personal"}
    org_groups = defaultdict(dict)
    for k, v in repo_commits.items():
        if v["source"] == "org" and v["org"]:
            org_groups[v["org"]][k] = v
    
    # 报告开头：AI 总结
    report = f"""📊 牛马日报 | {date_str} {weekday}

{strength}
{comment}
🏆 综合评分: {score} 分

🤖 AI 点评
{ai_summary}

📈 核心数据
📝 提交: {total_commits} 次
Push: {stats['push_events']} 次
🔀 PR: 创建 {stats['pr_created']} / 合并 {stats['pr_merged']} / 审查 {stats['pr_reviewed']} 个
📋 Issue: 创建 {stats['issues_created']} / 关闭 {stats['issues_closed']} 个
⭐ Star: {stats['stars']} | Fork: {stats['forks']} 次

💻 代码统计
📊 代码: +{total_additions} / -{total_deletions} 行
{code_bar}
📁 活跃仓库: {len(stats['repos_active'])} 个"""
    
    # 各组织仓库详情（只显示仓库名和统计，不显示具体 commit）
    for org_name, repos in org_groups.items():
        report += f"\n\n🏢 {org_name}"
        for repo_name, repo_stat in sorted(repos.items(), key=lambda x: x[1]["count"], reverse=True):
            short_name = repo_name.split("/")[-1]
            report += f"\n🔹 {short_name}: {repo_stat['count']} 次提交 | +{repo_stat['additions']}/-{repo_stat['deletions']} 行"
    
    # 个人仓库详情
    if personal_repos:
        report += f"\n\n👤 个人项目"
        for repo_name, repo_stat in sorted(personal_repos.items(), key=lambda x: x[1]["count"], reverse=True):
            short_name = repo_name.split("/")[-1]
            report += f"\n🔹 {short_name}: {repo_stat['count']} 次提交 | +{repo_stat['additions']}/-{repo_stat['deletions']} 行"
    
    report += f"\n💪 明天继续加油！"
    
    return report


def main():
    bj_tz = timezone(timedelta(hours=8))
    today = datetime.now(bj_tz).date()
    
    org_names = fetch_user_orgs()
    
    user_events = fetch_user_events(GITHUB_USERNAME, today)
    all_events = list(user_events)
    
    for org_name in org_names:
        org_events = fetch_org_events(org_name, today)
        all_events.extend(org_events)
    
    seen_ids = set()
    unique_events = []
    for event in all_events:
        event_id = event.get("id")
        if event_id not in seen_ids:
            seen_ids.add(event_id)
            unique_events.append(event)
    
    stats = analyze_events(unique_events, GITHUB_USERNAME, org_names)
    repo_commits = fetch_repo_commits(GITHUB_USERNAME, org_names, today)
    report = generate_report(stats, repo_commits, GITHUB_USERNAME, today)
    
    print(report)


if __name__ == "__main__":
    main()
