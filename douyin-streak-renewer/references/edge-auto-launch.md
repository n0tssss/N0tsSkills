# Edge 自动启动模式（Kimi Webbridge）

当 Kimi Webbridge 守护进程的 `extension_connected` 为 `false` 时，
自动启动 Edge 浏览器以激活扩展连接。

## Python 实现

```python
import subprocess, time, urllib.request, json

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
    edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
    subprocess.Popen(
        [edge_path, "--no-first-run"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    for i in range(20):
        time.sleep(1)
        if check_extension():
            print(f"Edge opened, extension connected ({i+1}s)")
            break
    else:
        print("Extension not connected after 20s")
```

## 注意事项

- 使用 `--no-first-run` 避免 Edge 首次启动引导页
- Kimi Webbridge 扩展需要已在 Edge 中安装（Extensions 目录下有对应 ID 的文件夹）
- 扩展通常需要载入一个网页后才会激活连接
- macOS 上路径固定为 `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`
- 使用 `subprocess.Popen`（非阻塞），不需要等待 Edge 退出
