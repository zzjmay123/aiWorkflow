---
name: ai-workflow
description: AI 资讯自动化工作流 — 自动抓取 10+ 科技媒体最新新闻，生成小红书风格图片，一键发布。支持早报/晚报自动区分。
license: MIT
compatibility: copaw
metadata:
  version: "1.0.0"
  tags: [ai, xiaohongshu, automation, news, media, content-creation]
  author: Jony (zzjmay123)
  copaw:
    emoji: "📰"
    requires:
      bins: [python3, playwright, xiaohongshu-cli]
      config:
        - ~/.copaw/config.json
---

# AI 资讯自动化工作流 | AI News Automation Workflow

自动抓取 10+ 家科技媒体最新 AI 新闻，一键生成小红书风格图片，自动发布到小红书。每天节省 2-3 小时找素材时间。

## ✨ 核心功能

- 🕸️ **智能抓取**：量子位、36 氪、IT 之家、虎嗅等 10+ 家媒体
- 🎨 **图片生成**：小红书风格图片生成器（3:4 比例，可自定义）
- 📱 **自动发布**：小红书官方 CLI，安全合规
- ⏰ **定时发布**：支持早报/晚报自动区分
- 📨 **飞书通知**：发布完成即时提醒

## 🚀 快速开始

### 一键安装

```bash
# 1. 克隆仓库
git clone https://github.com/zzjmay123/ai-workflow-skill.git
cd ai-workflow-skill

# 2. 运行安装脚本（自动安装所有依赖）
bash install.sh

# 3. 授权小红书（需扫码）
xiaohongshu auth login
```

### 快速运行

```bash
# 生成文本（可粘贴内容 + 小红书文案）
python scripts/ai_news_text_only.py

# 全自动发布（生成图片 + 发布小红书）
python scripts/auto_publish_final.py
```

## 📦 目录结构

```
ai-workflow-skill/
├── SKILL.md              # 技能说明（本文件）
├── install.sh            # 一键安装脚本
├── scripts/              # 核心脚本
│   ├── ai_news_text_only.py    # 文本生成
│   ├── auto_news_browser.py    # 新闻抓取
│   └── auto_publish_final.py   # 全自动发布
├── tools/                # 工具
│   └── ai-news-generator.html  # 图片生成器
├── docs/                 # 教程
│   ├── 01-安装指南.md
│   ├── 02-配置说明.md
│   └── 03-常见问题.md
└── assets/               # 资源文件
    └── screenshots/      # 示例截图
```

## 📖 详细文档

- [安装指南](docs/01-安装指南.md) - 环境准备与依赖安装
- [配置说明](docs/02-配置说明.md) - 个性化配置教程
- [常见问题](docs/03-常见问题.md) - FAQ 与故障排除

## ⚙️ 配置说明

### 1. 飞书配置（可选）

如需飞书通知，修改 `scripts/ai_news_text_only.py`：

```python
FEISHU_APP_ID = "你的飞书应用 ID"
FEISHU_APP_SECRET = "你的飞书应用密钥"
RECEIVE_USER_ID = "接收人飞书 ID"
```

### 2. 图片生成器配置

打开 `tools/ai-news-generator.html`，可修改：
- 图片尺寸（默认 540x720，3:4 比例）
- 每页显示条数（默认 2 条）
- 颜色主题（默认黑色）

### 3. 新闻源配置

修改 `scripts/auto_news_browser.py` 中的 `sources` 列表，可添加/删除/修改新闻源。

## 🎯 使用场景

- AI/科技自媒体日更
- 小红书批量运营
- 新闻资讯聚合展示
- 个人知识库自动更新

## ⚠️ 注意事项

1. 小红书发布需先完成账号认证
2. 飞书通知需配置应用凭证
3. 新闻源可能因网站改版需要调整
4. 建议先用测试账号验证流程
5. 系统内置防重复机制，每天只发布一次

## 🔧 故障排除

### 新闻抓取失败
- 检查网络连接
- 网站可能改版，需更新选择器
- 部分媒体有反爬机制，可降低抓取频率

### 图片生成空白
- 确保粘贴的内容格式正确
- 浏览器需支持 HTML5（Chrome/Edge 推荐）
- 检查 HTML 文件是否完整

### 发布失败
- 确认 `xiaohongshu auth login` 已成功
- 图片格式/大小不符合要求
- 文案包含敏感词

## 📞 技术支持

遇到问题？
- 查看 [常见问题](docs/03-常见问题.md)
- 提交 Issue 到 GitHub 仓库
- 联系作者获取一对一支持

## 📄 许可证

MIT License - 可自由使用、修改、分发。

---

**祝你使用愉快，早日爆单！** 🚀

## 变更日志

- **v1.0.0** - 初始版本
  - ✅ 10+ 家媒体新闻抓取
  - ✅ 小红书风格图片生成
  - ✅ 自动发布到小红书
  - ✅ 早报/晚报自动区分
  - ✅ 飞书通知支持
