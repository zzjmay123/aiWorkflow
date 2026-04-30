# 🎯 Pinchtab Browser Automation

> 通过 Pinchtab HTTP API 控制浏览器，稳定、低消耗的浏览器自动化方案

---

## ✅ 安装状态

| 组件 | 状态 | 位置 |
|------|------|------|
| Pinchtab 二进制 | ✅ 已安装 | `~/bin/pinchtab` |
| 启动脚本 | ✅ 已配置 | `~/bin/pinchtab-start.sh` |
| 停止脚本 | ✅ 已配置 | `~/bin/pinchtab-stop.sh` |
| Python 客户端 | ✅ 已配置 | `./scripts/pinchtab_client.py` |
| 测试脚本 | ✅ 已验证 | `./scripts/test-pinchtab.py` |

---

## 🚀 快速开始

### 1️⃣ 启动服务
```bash
~/bin/pinchtab-start.sh
```

### 2️⃣ 检查状态
```bash
curl http://localhost:9867/health
# 返回：{"mode":"dashboard","status":"ok"}
```

### 3️⃣ 运行测试
```bash
python3 ./scripts/test-pinchtab.py
```

### 4️⃣ 开始使用
```python
from pinchtab_client import PinchtabClient

client = PinchtabClient()
client.open("https://www.baidu.com")
snapshot = client.snapshot()
client.screenshot("page.png")
```

---

## 📖 详细文档

- **完整使用说明** → 查看 `SKILL.md`
- **Python 客户端** → `./scripts/pinchtab_client.py`
- **快速测试** → `./scripts/test-pinchtab.py`

---

## 🎯 常用操作

| 操作 | 代码示例 |
|------|---------|
| 打开网页 | `client.open("https://example.com")` |
| 获取快照 | `snapshot = client.snapshot()` |
| 截图 | `client.screenshot("page.png", full_page=True)` |
| 点击元素 | `client.click("e123")` |
| 输入文本 | `client.type("e456", "Hello")` |
| 按键盘 | `client.press_key("Enter")` |
| 查找元素 | `ref = client.find_element(text="登录")` |
| 等待元素 | `client.wait_for(ref="e789")` |

---

## 🛠️ 管理命令

```bash
# 启动服务
~/bin/pinchtab-start.sh

# 停止服务
~/bin/pinchtab-stop.sh

# 查看日志
cat /tmp/pinchtab.log

# 重启服务
~/bin/pinchtab-stop.sh && ~/bin/pinchtab-start.sh
```

---

## 🌐 访问地址

| 用途 | URL |
|------|-----|
| 健康检查 | http://localhost:9867/health |
| 管理界面 | http://localhost:9867/dashboard |
| API 端点 | http://localhost:9867 |

---

## ⚡ 与 browser_use 对比

**推荐使用 Pinchtab 的场景：**
- ✅ 需要长时间运行的自动化任务
- ✅ 需要保持登录态
- ✅ 需要多标签页管理
- ✅ browser_use 不稳定时
- ✅ 需要低 Token 消耗

**继续使用 browser_use 的场景：**
- 简单的单次页面抓取
- 需要 headed 模式演示
- 已有 Playwright 代码复用

---

## 📝 最佳实践

1. **使用前检查服务**：`client.health_check()`
2. **操作间加等待**：`time.sleep(1-3)` 或 `client.wait_for()`
3. **优先用 ref 定位**：比 selector 更稳定
4. **定期截图调试**：`client.screenshot("debug.png")`
5. **错误处理**：用 try-except 包裹关键操作

---

## 🆘 故障排查

### 服务无法启动
```bash
# 检查端口是否被占用
lsof -i :9867

# 查看日志
cat /tmp/pinchtab.log

# 重新启动
~/bin/pinchtab-stop.sh
~/bin/pinchtab-start.sh
```

### API 调用超时
- 增加 timeout 参数：`PinchtabClient(timeout=60)`
- 检查网络连接
- 确认服务运行：`curl http://localhost:9867/health`

### 元素找不到
- 先截图确认页面状态
- 获取快照查看实际元素结构
- 等待页面加载完成：`time.sleep(2)`

---

## 📚 资源链接

- 官方文档：https://pinchtab.com/docs
- GitHub: https://github.com/pinchtab/pinchtab
- 本地 Skill: `/Users/zhouzhenjiang/.copaw/active_skills/Pinchtab Browser Automation/`

---

**创建时间**: 2026-03-13  
**版本**: v1.0  
**状态**: ✅ 生产可用
