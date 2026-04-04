# Pinchtab Browser Automation

通过 Pinchtab HTTP API 控制浏览器，替代 browser_use 的 Playwright 方案。适用于需要稳定浏览器自动化的场景。

## 📦 什么是 Pinchtab

Pinchtab 是一个专为 AI 代理设计的轻量级浏览器控制工具，通过 HTTP API 提供浏览器自动化能力。

**优势：**
- ✅ 独立服务，不依赖 Playwright
- ✅ 低 Token 消耗（约 800 tokens/页）
- ✅ 支持无头/有头模式
- ✅ 多实例并行
- ✅ 结构化无障碍树（AI 友好）

---

## 🎯 何时使用

**触发场景：**
1. 需要打开网页获取内容
2. 需要截图、填表、点击等操作
3. 需要登录态保持
4. 需要多标签页管理
5. browser_use 不稳定时的备选方案

---

## 🚀 服务状态检查

```bash
# 检查服务是否运行
curl http://localhost:9867/health

# 如果未运行，启动服务
~/bin/pinchtab-start.sh
```

---

## 📖 API 使用指南

### 1️⃣ 打开网页

```bash
curl -X POST http://localhost:9867/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 2️⃣ 获取页面内容（无障碍树）

```bash
curl http://localhost:9867/snapshot
```

返回结构化的页面元素树，包含 ref、文本、角色等信息。

### 3️⃣ 截图

```bash
# 全屏截图
curl -X POST http://localhost:9867/screenshot \
  -H "Content-Type: application/json" \
  -d '{"full_page": true}' \
  --output screenshot.png

# 元素截图
curl -X POST http://localhost:9867/screenshot \
  -H "Content-Type: application/json" \
  -d '{"ref": "e123"}' \
  --output element.png
```

### 4️⃣ 点击元素

```bash
curl -X POST http://localhost:9867/click \
  -H "Content-Type: application/json" \
  -d '{"ref": "e123"}'
```

### 5️⃣ 输入文本

```bash
curl -X POST http://localhost:9867/type \
  -H "Content-Type: application/json" \
  -d '{"ref": "e123", "text": "Hello World"}'
```

### 6️⃣ 按键盘

```bash
curl -X POST http://localhost:9867/press_key \
  -H "Content-Type: application/json" \
  -d '{"key": "Enter"}'
```

### 7️⃣ 获取/切换标签页

```bash
# 列出所有标签页
curl http://localhost:9867/tabs

# 切换到指定标签页
curl -X POST http://localhost:9867/tabs \
  -H "Content-Type: application/json" \
  -d '{"action": "select", "index": 0}'
```

### 8️⃣ 等待

```bash
# 等待元素出现
curl -X POST http://localhost:9867/wait_for \
  -H "Content-Type: application/json" \
  -d '{"ref": "e123"}'

# 等待文本出现
curl -X POST http://localhost:9867/wait_for \
  -H "Content-Type: application/json" \
  -d '{"text": "登录成功"}'
```

---

## 🔧 Python 封装示例

```python
#!/usr/bin/env python3
"""Pinchtab 浏览器自动化客户端"""

import requests
import time

class PinchtabClient:
    def __init__(self, base_url="http://localhost:9867"):
        self.base_url = base_url
    
    def health_check(self):
        """检查服务状态"""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=5)
            return resp.json().get("status") == "ok"
        except:
            return False
    
    def open(self, url):
        """打开网页"""
        resp = requests.post(f"{self.base_url}/navigate", 
                            json={"url": url}, timeout=30)
        return resp.json()
    
    def snapshot(self):
        """获取页面快照"""
        resp = requests.get(f"{self.base_url}/snapshot", timeout=30)
        return resp.json()
    
    def screenshot(self, path="screenshot.png", full_page=False):
        """截图"""
        resp = requests.post(f"{self.base_url}/screenshot",
                            json={"full_page": full_page}, timeout=30)
        with open(path, 'wb') as f:
            f.write(resp.content)
        return path
    
    def click(self, ref):
        """点击元素"""
        resp = requests.post(f"{self.base_url}/click",
                            json={"ref": ref}, timeout=30)
        return resp.json()
    
    def type(self, ref, text):
        """输入文本"""
        resp = requests.post(f"{self.base_url}/type",
                            json={"ref": ref, "text": text}, timeout=30)
        return resp.json()
    
    def press_key(self, key):
        """按键盘"""
        resp = requests.post(f"{self.base_url}/press_key",
                            json={"key": key}, timeout=30)
        return resp.json()

# 使用示例
if __name__ == "__main__":
    client = PinchtabClient()
    
    if not client.health_check():
        print("❌ Pinchtab 服务未运行")
        exit(1)
    
    # 打开网页
    client.open("https://www.baidu.com")
    time.sleep(2)
    
    # 获取快照
    snapshot = client.snapshot()
    print("页面标题:", snapshot.get("title"))
    
    # 截图
    client.screenshot("test.png")
    print("✅ 截图已保存")
```

---

## 📝 完整工作流示例

### 百度搜索示例

```python
def baidu_search(keyword):
    """百度搜索"""
    client = PinchtabClient()
    
    # 1. 打开百度
    client.open("https://www.baidu.com")
    time.sleep(2)
    
    # 2. 获取快照找搜索框
    snapshot = client.snapshot()
    
    # 3. 找到搜索框 ref（假设是 e1）
    search_box_ref = find_element_by_aria_label(snapshot, "搜索")
    
    # 4. 输入关键词
    client.type(search_box_ref, keyword)
    
    # 5. 按回车
    client.press_key("Enter")
    time.sleep(3)
    
    # 6. 获取结果页
    result_snapshot = client.snapshot()
    
    # 7. 截图
    client.screenshot(f"baidu_{keyword}.png")
    
    return extract_search_results(result_snapshot)
```

---

## ⚠️ 注意事项

1. **服务必须先启动**：使用前确保 `~/bin/pinchtab-start.sh` 已运行
2. **端口配置**：默认 9867，可通过脚本参数修改
3. **超时设置**：API 调用建议设置 30 秒超时
4. **元素定位**：优先使用 ref，其次 selector
5. **等待机制**：操作间适当 sleep，或用 wait_for

---

## 🔐 安全配置（可选）

如需认证，设置环境变量：

```bash
export PINCHTAB_TOKEN="your-secret-token"
~/bin/pinchtab --port 9867 --token $PINCHTAB_TOKEN
```

调用时加 Header：
```bash
curl -H "Authorization: Bearer your-token" http://localhost:9867/health
```

---

## 🆚 与 browser_use 对比

| 特性 | Pinchtab | browser_use (Playwright) |
|------|----------|-------------------------|
| 部署方式 | 独立服务 | Python 库 |
| Token 消耗 | 低 (~800/页) | 中 |
| 稳定性 | 高 | 中 |
| 多实例 | 支持 | 较复杂 |
| 无障碍树 | ✅ 原生支持 | ❌ 需额外处理 |
| 学习曲线 | 低 (HTTP API) | 中 |

---

## 📚 相关资源

- 本地安装：`/Users/zhouzhenjiang/bin/pinchtab`
- 启动脚本：`/Users/zhouzhenjiang/bin/pinchtab-start.sh`
- 停止脚本：`/Users/zhouzhenjiang/bin/pinchtab-stop.sh`
- 日志文件：`/tmp/pinchtab.log`
- 官方文档：https://pinchtab.com/docs
- GitHub: https://github.com/pinchtab/pinchtab

---

## 🎯 快速开始

```bash
# 1. 启动服务
~/bin/pinchtab-start.sh

# 2. 检查状态
curl http://localhost:9867/health

# 3. 打开网页
curl -X POST http://localhost:9867/navigate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.baidu.com"}'

# 4. 获取快照
curl http://localhost:9867/snapshot
```

搞定！🎉
