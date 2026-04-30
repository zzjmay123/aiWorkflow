# web-access Skill 安装说明

## 文件结构

```
web-access/
├── SKILL.md                          # 技能主文档（必读）
├── scripts/
│   ├── cdp-proxy.mjs                 # CDP 代理服务器
│   ├── check-deps.sh                 # 环境检查脚本
│   └── match-site.sh                 # 站点经验匹配脚本
└── references/
    ├── cdp-api.md                    # CDP API 参考文档
    └── site-patterns/
        └── xiaohongshu.com.md        # 站点经验（示例）
```

## 激活步骤

### 1. 环境要求

- **Node.js 22+**（或 Node.js 18+ 并安装 `ws` 模块）
- **Google Chrome**（或 Chromium）

### 2. Chrome 设置

打开 Chrome，在地址栏输入：
```
chrome://inspect/#remote-debugging
```

勾选 **"Allow remote debugging for this browser instance"**

### 3. 测试连接

运行环境检查脚本：
```bash
bash /Users/zhouzhenjiang/.copaw/workspaces/default/active_skills/web-access/scripts/check-deps.sh
```

预期输出：
```
node: ok (v22.x.x)
chrome: ok (port 9222)
proxy: ready
```

### 4. 在 CoPaw 中启用

本技能已安装在 CoPaw 工作区的 `active_skills/web-access/` 目录。

当用户提到以下场景时，自动加载此技能：
- 搜索信息、查看网页内容
- 访问需要登录的网站
- 操作网页界面、抓取社交媒体内容
- 读取动态渲染页面
- 任何需要真实浏览器环境的网络任务

## 快速开始

### 启动 CDP Proxy（手动）
```bash
node /Users/zhouzhenjiang/.copaw/workspaces/default/active_skills/web-access/scripts/cdp-proxy.mjs &
```

### 测试 API
```bash
# 健康检查
curl http://localhost:3456/health

# 列出所有 tab
curl http://localhost:3456/targets

# 打开新页面
curl "http://localhost:3456/new?url=https://example.com"
```

## 注意事项

1. **Proxy 持续运行**：启动后不建议主动停止，重启需要 Chrome 重新授权
2. **用户登录态**：CDP 模式使用用户日常 Chrome，天然携带登录态
3. **最小侵入**：所有操作在后台 tab 进行，不干扰用户已有 tab
4. **任务结束清理**：用 `/close` 关闭自己创建的 tab

## 故障排查

| 问题 | 解决 |
|------|------|
| `node: missing` | 安装 Node.js 22+ |
| `chrome: not connected` | 打开 chrome://inspect 并勾选 Allow remote debugging |
| `proxy: connecting...` 超时 | 检查 Chrome 是否有授权弹窗，点击允许 |
| 端口被占用 | 已有 proxy 实例可直接复用 |

## 参考资料

- [GitHub 项目](https://github.com/eze-is/web-access)
- [微信文章详解](https://mp.weixin.qq.com/s/rps5YVB6TchT9npAaIWKCw)
- 作者：一泽 Eze (@eze-is)
