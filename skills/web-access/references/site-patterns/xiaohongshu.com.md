---
domain: xiaohongshu.com
aliases: [小红书，RedNote，RED]
updated: 2026-03-20
---
## 平台特征

- **强反爬**：静态 API 基本不可用，必须使用浏览器 CDP 模式
- **登录墙**：未登录状态下大部分内容不可见，需用户提前登录
- **动态加载**：内容通过滚动懒加载，需主动触发
- **URL 结构**：笔记 URL 格式为 `xiaohongshu.com/explore/{noteId}`

## 有效模式

- **CDP 直接访问**：用 `/new` 打开笔记 URL，然后 `/eval` 提取内容
- **滚动加载**：用 `/scroll?direction=bottom` 触发更多内容
- **内容提取**：从 DOM 直接提取标题、正文、图片 URL，避免截图

## 已知陷阱

- **不要搜索**：站内搜索功能对自动化不友好，直接访问已知 URL
- **不要依赖 API**：官方 API 不公开，第三方 API 不稳定
- **登录状态**：如遇到登录提示，告知用户在 Chrome 中登录后继续，不要尝试自动化登录
