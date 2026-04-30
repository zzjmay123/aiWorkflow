# Long-Term Memory

## 用户信息
- **姓名**: 周振江
- **配偶**: 张月皎 | **孩子**: 蔡麒铭
- **交互风格**: 结果导向，要求直接可运行方案；对设计还原要求高（像素级），期望确定性操作（说几条就几条），偏好显式控制而非随机/自动

---

## 项目一：AI 资讯自动化发布系统

### 核心架构
| 组件 | 用途 |
|---|---|
| `auto_publish_final.py` | 全自动发布（文本生成 → 下载图片 → CLI 发布 → 飞书通知） |
| `ai-news-generator.html` | 小红书图片生成器（HTML/CSS → 截图） |
| `auto_news_browser.py` | 新闻抓取（纯标准库，无第三方依赖） |
| `xiaohongshu-cli` | 小红书 CLI 发布工具 |
| `feishu-file-sender` | 飞书通知技能 |

### 运行策略（当前生效）
- **定时**: 每日 08:00，拦截窗口 06:00–12:00（`>=12:00` 自动退出）
- **防重复**: 锁文件 `/tmp/xiaohongshu_publish_lock` + 运行前删除当天旧文本 + `news_history.json` 记录已发布
- **超时控制**: `MAX_RETRIES=3`, `STEP_TIMEOUT=120s`, `GLOBAL_TIMEOUT=300s`
- **标题**: "爆款标题库"动态生成（突破/重磅/警惕等前缀）
- **最后成功**: 2026-04-27, 笔记 ID `69eeb533000000001f000712`

### 图片规格与设计系统
- **画布**: 540×720 px（3:4 比例）
- **分页**: **2 条资讯/页**（用户确认偏好）
- **当前主题**: **Tech Blue（科技蓝）** — 默认主题
  - 主色: `#2563EB`（蓝）/ `#0F172A`（深灰）/ `#475569`（中灰）/ `#94A3B8`（浅灰）
  - 背景: 浅蓝渐变 + 科技线条 + 底部水波纹 + 地球仪 SVG
  - 头部: 标题双色调（"全球"深色+"早报"蓝色），日期标签
  - 卡片: 蓝色编号方块、AI Insight 星标标签、来源带文档图标
  - 卡片圆角: **24px**
- **字体**: `Noto Sans SC`（替代 Plus Jakarta Sans，中文适配更好）
- **设计还原原则**: 以用户参考图为准进行像素级还原；精确取色→测量间距→组件化→装饰元素→对比验证；不凭印象写样式

> **CL4R1T4S 原则（适度适用）**: ❌ 禁用 Emoji/"AI味"配色；✅ CSS Variables 保证一致性；✅ 分页限制 720px 高度
> **注**: 用户提供的参考图本身含微妙渐变，CL4R1T4S 需灵活适配，核心是"企业/SaaS 感"而非教条。

### 新闻源与文案策略
- **优先级**: 官方 RSS/博客 > 英文科技媒体 > 中文科技媒体（中文源有数小时延迟）
- **时效**: 仅推送 24–72 小时内新闻；必须有真实可访问 URL
- **文案**: <1000 字；话题标签前置，链接汇总放末尾；标题 >45 字截断加 "..."；极简清单体

### 关键路径与配置
- **工作区**: `/Users/zhouzhenjiang/.copaw/workspaces/5MUwUP/`
- **HTML 生成器**: `/Users/zhouzhenjiang/workspace/aiWorkflow/ai-news-generator.html`
- **图片下载**: `WORK_DIR/output/downloads/`（非 `~/Downloads`）
- **Cookie**: `~/.xiaohongshu-cli/cookies.json`（TTL 7 天）
- **发布命令**: `python3 -m xhs_cli.cli post --title ... --body ... --images ...`（需设 `PYTHONPATH`）
- **xhs_cli 包**: `~/.local/pipx/venvs/xiaohongshu-cli/lib/python3.10/site-packages`
- **飞书**: 运营--Jony（`cli_a947f3a013215ccf`）→ 接收人 `ou_975690183c044ff01e03b1d66fb98df9`
- **小红书**: Jony（`red_id: 26457944049`）

---

## 项目二：亲密卡 AI 卡面生成

- **流程**: 列表 → 上传 → 选风格 → 生成 → 结果 → 应用/赠送
- **技术**: 纯 Vanilla JS/HTML 单文件，零外部 CDN；图标用内联 SVG
- **设计**: Consumer 风格（紫色/粉色渐变、Emoji、大圆角 — 与资讯项目明确隔离）
- **关键决策**: 沙箱浏览器拦截外部 API（Pollinations），改用 Canvas API 本地模拟
- **状态**: ✅ 高保真原型已完成；接入真实 AI API 需后端支持
- **文件**: `/Users/zhouzhenjiang/Documents/copawMedia/intimate-card-demo.html`

---

## Sandbox 环境限制与通用策略

| 限制 | 应对策略 |
|---|---|
| `pip install` 失败（只读文件系统） | 仅用 Python 标准库（`re`, `xml.etree`, `urllib`, `json`） |
| 外部 CDN 加载失败（`ERR_CONNECTION_CLOSED`） | 内联 SVG / data URI 替代外部资源 |
| `file://` 协议空白页 | 必须通过 HTTP 本地服务访问 |
| `~/Downloads` 文件过多导致超时 | 使用工作区内相对路径 |
| Cookie 提取超时/卡住 | 更新 `cookies.json` 的 `saved_at` 跳过浏览器刷新；彻底失效需用户 Mac 手动登录 |
| `http.server` 端口冲突 | 先 `pkill` 清理，动态检查可用端口 |
| 定时任务执行但用户未收到 | session_id 过期，需更新 cron 的 session_id |
| 飞书消息显示为其他机器人 | 脚本优先读取 `agent.json` 中的配置 |
| 飞书文件链接不可点击 | 改用飞书文本消息发送（非 txt 纯文本格式） |

---

## 全局用户偏好
- ✅ 仅推送文本，不自动生成图片
- ✅ 生成完直接发飞书，无需确认
- ✅ 使用"运营--Jony"机器人（非"小江同学"）
- ✅ 链接放正文中（可点击），末尾保留汇总
- ✅ 新闻项目偏好企业级/SaaS 审美（Linear 风格，但允许微妙渐变）
- ✅ 说几条就几条，不要自作主张更改
