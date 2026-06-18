#!/usr/bin/env python3
"""
牛马日报/周报 HTML 生成器
将 github-summary.py 的文本输出转为精美 HTML
"""

import sys
import os
import json
import subprocess
import re
from datetime import datetime

TEMPLATE_DIR = os.path.expanduser("~/.hermes/skills/N0tsSkills/github-niuma-daily/templates")
OUTPUT_DIR = os.path.expanduser("~/.hermes/media")


def parse_daily_report(text):
    """解析日报文本输出为结构化数据"""
    data = {
        "type": "daily",
        "date": "",
        "weekday": "",
        "status_emoji": "",
        "status_text": "",
        "score": 0,
        "comment": "",
        "commits": 0,
        "push": 0,
        "pr_created": 0,
        "pr_merged": 0,
        "issue_created": 0,
        "issue_closed": 0,
        "stars": 0,
        "forks": 0,
        "repos_count": 0,
        "additions": 0,
        "deletions": 0,
        "repos": []
    }
    
    lines = text.strip().split('\n')
    
    for line in lines:
        # 解析标题行: 📊 牛马日报 | 2026.06.15 周一
        m = re.match(r'📊 牛马[日周]报 \| (\d{4}\.\d{2}\.\d{2}) (\S+)', line)
        if m:
            data["date"] = m.group(1)
            data["weekday"] = m.group(2)
            data["type"] = "daily" if "日报" in line else "weekly"
            continue
        
        # 解析状态行: 🔥🔥🔥 顶级牛马 | 74 分
        m = re.match(r'(.+?) (.+?) \| (\d+) 分', line)
        if m:
            data["status_emoji"] = m.group(1).strip()
            data["status_text"] = m.group(2).strip()
            data["score"] = int(m.group(3))
            continue
        
        # 解析AI点评（状态行的下一行）
        if data["status_text"] and not data["comment"] and line.strip() and not line.startswith('📝') and not line.startswith('💻'):
            data["comment"] = line.strip()
            continue
        
        # 解析提交数据: 📝 提交 27 · Push 0
        m = re.match(r'📝 提交 (\d+) · Push (\d+)', line)
        if m:
            data["commits"] = int(m.group(1))
            data["push"] = int(m.group(2))
            continue
        
        # 解析代码行: 💻 +7505 / -2575 行
        m = re.match(r'💻 \+([\d,]+) / -([\d,]+) 行', line)
        if m:
            data["additions"] = int(m.group(1).replace(',', ''))
            data["deletions"] = int(m.group(2).replace(',', ''))
            continue
        
        # 解析PR/Issue: 🔀 PR: 0建0合 | 📋 Issue: 0建0关
        m = re.match(r'🔀 PR: (\d+)建(\d+)合 \| 📋 Issue: (\d+)建(\d+)关', line)
        if m:
            data["pr_created"] = int(m.group(1))
            data["pr_merged"] = int(m.group(2))
            data["issue_created"] = int(m.group(3))
            data["issue_closed"] = int(m.group(4))
            continue
        
        # 解析Star/Fork/仓库: ⭐ 0 · 🍴 0 · 📁 3个仓库
        m = re.match(r'⭐ (\d+) · 🍴 (\d+) · 📁 (\d+)个仓库', line)
        if m:
            data["stars"] = int(m.group(1))
            data["forks"] = int(m.group(2))
            data["repos_count"] = int(m.group(3))
            continue
        
        # 解析仓库行: N0tsLabs/NutBuddy 24次 ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ +7419/-2572
        # 注意：必须用 [\w\-]+/[\w\-]+ 匹配 org/repo 格式，不能用 \S+?
        m = re.match(r'([\w\-]+/[\w\-]+)\s+(\d+)次\s+.+?\s+([\+\-][\d,]+/[\+\-][\d,]+)', line)
        if m:
            repo_name = m.group(1)
            count = int(m.group(2))
            diff = m.group(3)
            # 解析 +/- 行
            diff_m = re.match(r'\+([\d,]+)/\-([\d,]+)', diff)
            additions = int(diff_m.group(1).replace(',', '')) if diff_m else 0
            deletions = int(diff_m.group(2).replace(',', '')) if diff_m else 0
            data["repos"].append({
                "name": repo_name,
                "count": count,
                "additions": additions,
                "deletions": deletions
            })
            continue
    
    return data


def format_number(n):
    """格式化数字: 1234 -> 1.2K"""
    if n >= 1000:
        return f"{n/1000:.1f}K".replace('.0K', 'K')
    return str(n)


def generate_html(data):
    """根据数据生成 HTML"""
    # 计算进度条百分比
    max_count = data["repos"][0]["count"] if data["repos"] else 1
    total = data["additions"] + data["deletions"]
    add_pct = (data["additions"] / total * 100) if total > 0 else 100
    del_pct = (data["deletions"] / total * 100) if total > 0 else 0
    
    # 生成仓库HTML
    repos_html = ""
    for i, repo in enumerate(data["repos"][:3]):
        rank_class = "rank-1" if i == 0 else ""
        bar_width = (repo["count"] / max_count * 100) if max_count > 0 else 0
        full_name = repo["name"]
        
        repos_html += f'''
  <div class="repo-card">
    <div class="repo-rank {rank_class}">{i+1}</div>
    <div class="repo-info">
      <div class="repo-name" title="{full_name}">{full_name}</div>
      <div class="repo-bar"><div class="repo-bar-fill" style="width: {bar_width}%"></div></div>
      <div class="repo-diff">+{repo["additions"]:,} / -{repo["deletions"]:,}</div>
    </div>
    <div class="repo-count">{repo["count"]}<span>次</span></div>
  </div>'''
    
    if not data["repos"]:
        repos_html = '<div class="empty-state">今日无提交</div>'
    
    # 选择模板
    template_file = "daily.html" if data["type"] == "daily" else "weekly.html"
    template_path = os.path.join(TEMPLATE_DIR, template_file)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 替换占位符
    html = template.replace("{{DATE}}", data["date"])
    html = html.replace("{{WEEKDAY}}", data["weekday"])
    html = html.replace("{{STATUS_BADGE}}", f'{data["status_emoji"]} {data["status_text"]}')
    html = html.replace("{{SCORE}}", str(data["score"]))
    html = html.replace("{{COMMENT}}", data["comment"])
    html = html.replace("{{COMMITS}}", str(data["commits"]))
    html = html.replace("{{CODE_LINES}}", format_number(data["additions"] + data["deletions"]))
    html = html.replace("{{PR_COUNT}}", str(data["pr_created"] + data["pr_merged"]))
    html = html.replace("{{REPOS_COUNT}}", str(data["repos_count"]))
    html = html.replace("{{ADDITIONS}}", f"+{data['additions']:,}")
    html = html.replace("{{DELETIONS}}", f"-{data['deletions']:,}")
    html = html.replace("{{ADD_PCT}}", f"{add_pct:.1f}")
    html = html.replace("{{DEL_PCT}}", f"{del_pct:.1f}")
    html = html.replace("{{REPOS_HTML}}", repos_html)
    
    # 保存HTML
    filename = f"report-{data['date'].replace('.', '')}.html"
    output_path = os.path.join(OUTPUT_DIR, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path


def main():
    # 运行 github-summary.py 获取文本输出
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    weekly = "--week" in sys.argv
    
    cmd = ["python3", os.path.expanduser("~/.hermes/scripts/github-summary.py")]
    if weekly:
        cmd.append("--week")
    if date_arg and date_arg != "--week":
        cmd.extend(["--date", date_arg])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running github-summary: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    report_text = result.stdout
    
    # 解析数据
    data = parse_daily_report(report_text)
    
    # 生成HTML
    html_path = generate_html(data)
    
    # 输出JSON供后续截图使用
    print(json.dumps({
        "html_path": html_path,
        "report_text": report_text,
        "data": data
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
