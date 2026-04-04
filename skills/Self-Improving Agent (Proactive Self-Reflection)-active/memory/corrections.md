# 纠正与教训

## 2026-03-17

### Pinchtab 截图 API 问题
- **问题**: Pinchtab 截图 API 使用 POST 方法但返回 JSON 格式 (`{"base64": "...", "format": "jpeg"}`)，而非直接返回图片二进制
- **解决**: 使用 Python 客户端 (`pinchtab_client.py`) 的 `screenshot()` 方法可正确处理
- **教训**: 直接使用 curl 调用截图 API 会失败，优先使用封装好的 Python 客户端
- **替代方案**: 若只需股价数据，直接从 `snapshot` 的 `nodes` 数组中提取 `LayoutTableCell` 元素即可，无需截图

### 小米股票数据提取技巧
- **数据源**: 东方财富网港股页面 (`quote.eastmoney.com/hk/01810.html`)
- **关键元素**: `LayoutTableCell` 角色包含完整股价数据（今开、最高、最低、昨收、成交量、成交额、总市值、市盈率等）
- **提取方法**: 解析 `snapshot.nodes` 数组，查找 `name` 字段包含"最新价"、"涨跌幅"、"成交量"等关键词的元素
- **优势**: 比截图更稳定，比网页 scraping 更可靠（无障碍树结构清晰）
