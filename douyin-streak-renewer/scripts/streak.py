#!/usr/bin/env python3
"""
Douyin Streak Renewer — sends "自动续火花啦！" to streak conversations daily.
Uses Kimi Webbridge HTTP API at http://127.0.0.1:10086/command
No LLM needed — purely scripted.
"""

import json
import time
import urllib.request
import urllib.error
import sys

API = "http://127.0.0.1:10086/command"
SESSION = "douyin-streak"

# ── Edit these to match your conversations (uses includes() match) ──
CONVERSATIONS = [
    "宝宝呢",
    "小笨蛋宝宝",
]
# When a name matches multiple conversations (e.g. "小笨蛋宝宝" matches 1号 and 2号),
# the script sends to ALL matching conversations.
# ───────────────────────────────────────────────────────────────────

MESSAGE = "自动续火花啦！"
RETRIES = 3
RETRY_DELAY = 2


def cmd(action, args=None):
    """Call Kimi Webbridge API."""
    payload = {"action": action, "session": SESSION}
    if args:
        payload["args"] = args
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        API, data=body,
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        return {"ok": False, "error": str(e)}


def evaluate(js_code):
    """Run JS in page context."""
    result = cmd("evaluate", {"code": js_code})
    data = result.get("data", {})
    if data.get("type") == "string":
        return data.get("value")
    return data


def click_conversation(name):
    """Click a conversation item by name using native MouseEvents (React-safe).
    Returns 'NOT_FOUND' if no match, or 'OK' on click.
    """
    safe_name = name.replace("\\", "\\\\").replace("'", "\\'")
    js = (
        "(() => {"
        "const items = Array.from(document.querySelectorAll("
        '".conversationConversationItemwrapper"));'
        "const el = items.find(e => {"
        "const title = e.querySelector("
        '".conversationConversationItemtitle");'
        "return title && title.textContent.trim().includes('"
        + safe_name +
        "');"
        "});"
        "if (!el) return 'NOT_FOUND';"
        "const r = el.getBoundingClientRect();"
        "el.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, clientX: r.left + 10, clientY: r.top + 30}));"
        "el.dispatchEvent(new MouseEvent('mouseup',   {bubbles: true, clientX: r.left + 10, clientY: r.top + 30}));"
        "el.dispatchEvent(new MouseEvent('click',     {bubbles: true, clientX: r.left + 10, clientY: r.top + 30}));"
        "return 'OK';"
        "})()"
    )
    return evaluate(js)


def find_all_matching(name):
    """Find ALL conversation items whose title includes the given name.
    Returns list of indices (nth-child position among matches)."""
    safe_name = name.replace("\\", "\\\\").replace("'", "\\'")
    js = (
        "(() => {"
        "const items = Array.from(document.querySelectorAll("
        '".conversationConversationItemwrapper"));'
        "const matching = items.filter(e => {"
        "const title = e.querySelector("
        '".conversationConversationItemtitle");'
        "return title && title.textContent.trim().includes('"
        + safe_name +
        "');"
        "});"
        "return matching.length.toString();"
        "})()"
    )
    result = evaluate(js)
    try:
        return int(result) if result and result.isdigit() else 0
    except (ValueError, TypeError):
        return 0


def fill_and_send():
    """Fill the message input and dispatch Enter to send."""
    r = cmd("fill", {"selector": "div[contenteditable=true]", "value": MESSAGE})
    if not r.get("data", {}).get("success"):
        return False
    time.sleep(0.3)
    r = evaluate(
        "(() => {"
        "const el = document.querySelector('div[contenteditable=true]');"
        "if (!el) return 'NO_INPUT';"
        "el.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true}));"
        "el.dispatchEvent(new KeyboardEvent('keyup',   {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true}));"
        "return 'OK';"
        "})()"
    )
    return r == "OK"


def wait_for_panel(timeout=8):
    """Wait until the right panel shows a conversation (non-empty)."""
    for _ in range(timeout):
        r = evaluate(
            "document.querySelector('[class*=RightPanel]')"
            "?.innerText?.substring(0,10) || ''"
        )
        if r and len(r) > 1:
            return True
        time.sleep(1)
    return False


def main():
    results = []

    # ── Health check ──
    try:
        req = urllib.request.Request(API, method="GET")
        urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError:
        pass
    except Exception as e:
        print(f"\u274c Kimi Webbridge daemon not reachable: {e}")
        print("   Run: ~/.kimi-webbridge/bin/kimi-webbridge start")
        sys.exit(1)

    # ── Check extension connection; launch Edge if needed ──
    def check_extension():
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:10086/status", method="GET"
            )
            resp = urllib.request.urlopen(req, timeout=5)
            status = json.loads(resp.read())
            return status.get("extension_connected", False)
        except Exception:
            return False

    if not check_extension():
        print("  Extension not connected. Launching Edge browser...")
        import subprocess
        edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        subprocess.Popen(
            [edge_path, "--no-first-run"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        # Wait up to 20 seconds for extension to connect
        for i in range(20):
            time.sleep(1)
            if check_extension():
                print(f"  Edge opened, extension connected ({i+1}s)")
                break
        else:
            print("\u26a0\ufe0f  Edge launched but extension not connected after 20s.")
            print("   \u8bf7\u624b\u52a8\u786e\u8ba4 Kimi Webbridge \u6269\u5c55\u5df2\u5b89\u88c5\u5e76\u542f\u7528\u3002")
            sys.exit(1)

    # ── Open Douyin chat ──
    print("\U0001f504 Opening Douyin chat...")
    r = cmd("navigate", {"url": "https://www.douyin.com/chat?isPopup=1", "newTab": True})
    if not r.get("data", {}).get("success"):
        print("\u274c Failed to navigate to Douyin chat")
        sys.exit(1)
    time.sleep(2)

    # ── Send to each conversation ──
    for name in CONVERSATIONS:
        match_count = find_all_matching(name)
        if match_count == 0:
            print(f"  \u2192 {name}... \u274c not found")
            results.append((name, "\u26a0\ufe0f Not found"))
            continue

        for idx in range(match_count):
            label = f"{name} #{idx+1}" if match_count > 1 else name
            print(f"  \u2192 {label}...", end=" ", flush=True)

            for attempt in range(RETRIES):
                # Re-find and click the first matching item each time
                # (items shift when one is clicked but they stay in list order)
                click_result = click_conversation(name)

                if click_result == "NOT_FOUND":
                    if attempt < RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    print("\u274c not found")
                    results.append((label, "\u26a0\ufe0f Not found"))
                    break

                if not wait_for_panel():
                    if attempt < RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    print("\u274c panel timeout")
                    results.append((label, "\u26a0\ufe0f Panel timeout"))
                    break

                time.sleep(0.5)

                if fill_and_send():
                    results.append((label, "\u2705 Sent"))
                    print("\u2705")
                    break
                else:
                    if attempt < RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    print("\u274c send failed")
                    results.append((label, "\u26a0\ufe0f Send failed"))

    # ── Close session ──
    cmd("close_session")

    # ── Summary ──
    print()
    for name, status in results:
        print(f"{status} {name}")

    failed = [n for n, s in results if "\u274c" in s or "\u26a0" in s]
    if failed:
        print(f"\n\u26a0\ufe0f  {len(failed)}/{len(results)} conversations had issues.")
    else:
        print(f"\n\u2728 \u7eed\u706b\u82b1\u4efb\u52a1\u5b8c\u6210\uff01\u5168\u90e8 {len(results)} \u4e2a\u5df2\u53d1\u9001 \u2713")


if __name__ == "__main__":
    main()
