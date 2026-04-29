# Long-Term Memory

## 用户信息
- **姓名**: 周振江
- **配偶**: 张月皎 | **孩子**: 蔡麒铭
- **交互风格**: 结果导向，要求直接可运行方案；会立即查看效果，空白/报错会引起不满

---

## 项目一：AI 资讯自动化

### 系统架构
| 组件 | 用途 |
|---|---|
| `ai_news_text_only.py` | 文本生成（抓取媒体 → 生成文本+小红书文案） |
| `ai-news-generator.html` | 小红书图片生成器（支持 `?theme=random` 动态换肤） |
| `auto_publish_final.py` | 全自动发布（下载图片 → CLI 发布 → 飞书通知） |
| `xiaohongshu-cli` | 小红书 CLI 工具 v0.6.4 |
| `feishu-file-sender` | 飞书文件/消息发送技能 |

### 发布策略（当前生效）
- **定时**: 仅早 8:00 执行
- **防重复**: 运行前强制删除当天旧文本文件；`news_history.json` 记录已发布标题/URL
- **时间拦截**: `>=12:00` 自动退出
- **标题**: "爆款标题库"动态生成（突破/重磅/警惕等前缀）

### 设计系统：CL4R1T4S（企业级，仅限资讯项目）
- ❌ 禁用渐变、Emoji、"AI味"配色
- ✅ 圆角仅 `4px` / `8px`；字体 `Plus Jakarta Sans`
- ✅ CSS Variables（Design Tokens）保证一致性
- ✅ 分页：每页 3 条新闻（720px 高度限制）
- **已实现 3 主题**（`?theme=random` 切换）：Indigo Professional、Minimal Black、Mint

> **设计上下文隔离**：资讯项目 = CL4R1T4S（企业/SaaS 风，类 Linear）；亲密卡项目 = Consumer 风格（渐变、Emoji、大圆角）。两者不可混用。

### 新闻源策略
- **优先级**: 官方 RSS/博客 > 英文科技媒体 > 中文科技媒体
- **中文媒体**（量子位、36氪、机器之心等）存在数小时延迟，重大新闻先在英文源出现
- **时效**: 仅推送 24-72 小时内新闻
- **链接**: 所有新闻必须有真实可访问 URL

### 小红书文案规范
- 总字数 < 1000 字；话题标签前置，链接汇总放末尾
- 标题截断：> 45 字加 "..."；极简清单体

### 关键配置
- **工作区**: `/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/agent.json`
- **飞书**: 运营--Jony（`cli_a947f3a013215ccf`）→ 接收人 `ou_975690183c044ff01e03b1d66fb98df9`
- **小红书**: Jony（`red_id: 26457944049`）
- **输出**: `output/text/`

---

## 项目二：亲密卡 AI 卡面生成

- **流程**: 列表 → 上传 → 选风格 → 生成 → 结果 → 应用/赠送
- **技术**: 纯 Vanilla JS/HTML 单文件，零外部 CDN；图标用内联 SVG
- **设计**: Consumer 风格（紫色/粉色渐变、Emoji、大圆角 — 明确覆盖 CL4R1T4S）
- **关键决策**: 沙箱浏览器拦截外部 API（Pollinations），改用 Canvas API 本地模拟
- **状态**: ✅ 高保真原型已完成；接入真实 AI API 需后端支持
- **文件**: `/Users/zhouzhenjiang/Documents/copawMedia/intimate-card-demo.html`

---

## 全局用户偏好
- ✅ 仅推送文本，不自动生成图片
- ✅ 生成完直接发飞书，无需确认
- ✅ 使用"运营--Jony"机器人（非"小江同学"）
- ✅ 链接放正文中（可点击），末尾保留汇总
- ✅ 新闻项目偏好企业级/SaaS 审美（Linear 风格）

---

## 环境与排障速查

| 场景 | 原因 | 解决 |
|---|---|---|
| `pip install` 失败 | SSL/代理限制 | 仅用 Python 标准库（`xml.etree`, `urllib`, `json`） |
| 外部 CDN 加载失败 | `net::ERR_CONNECTION_CLOSED` | 内联 SVG / data URI 替代外部资源 |
| `file://` 协议空白页 | Playwright 安全策略 | 必须通过 HTTP 本地服务访问 |
| `http.server` 挂起 | 端口冲突 | 先 `pkill` 清理，动态检查可用端口 |
| 定时任务执行但用户未收到 | session_id 过期 | 更新 cron 任务的 session_id |
| 飞书消息显示为其他机器人 | 使用全局配置 | 脚本优先读取 `agent.json` |
| 飞书文件链接不可点击 | txt 纯文本格式 | 改用飞书文本消息发送 |
