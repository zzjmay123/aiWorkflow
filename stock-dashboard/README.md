# 股票大盘展示系统

A股技术面分析 + 人气指标推荐的股票展示平台

## 功能特性

- **大盘概览**：市场涨跌统计、涨停跌停、成交额TOP10
- **我的关注**：自定义关注股票列表，实时查看技术指标
- **每日推荐**：基于人气榜 + 上升趋势 + 放量筛选的推荐股票
- **技术分析**：MA/MACD/KDJ/RSI/BOLL等经典指标
- **K线图**：交互式K线图表，支持缩放和指标切换

## 筛选逻辑

每日推荐股票筛选条件：
1. 东方财富人气榜前200名
2. 上升趋势（均线多头排列或价格在MA20上方）
3. 近3天平均成交量 ≥ 前5天平均成交量的3倍

## 技术栈

- **后端**：Python + FastAPI + akshare
- **前端**：React + Vite + Ant Design + ECharts

## 快速开始

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt --break-system-packages
```

### 2. 启动后端服务

```bash
cd backend
python -m app.main
```

后端服务运行在 http://localhost:8000

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端服务

```bash
cd frontend
npm run dev
```

前端服务运行在 http://localhost:3000

## API接口

| 接口 | 说明 |
|------|------|
| GET /api/market/overview | 市场概览（涨跌统计） |
| GET /api/indices | 主要指数实时数据 |
| GET /api/popularity/recommended | 人气推荐股票 |
| GET /api/stock/{symbol} | 股票详情和技术指标 |
| GET /api/stock/search?keyword=xxx | 搜索股票 |
| GET /api/watchlist?symbols=000001,600000 | 关注列表技术指标 |

## 项目结构

```
stock-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py      # REST API路由
│   │   ├── services/
│   │   │   ├── data_fetcher.py  # 数据获取（akshare）
│   │   │   ├── indicator.py     # 技术指标计算
│   │   │   └── screener.py      # 人气筛选引擎
│   │   └── main.py            # FastAPI入口
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/               # API请求封装
    │   ├── components/        # React组件
    │   │   ├── MarketOverview.jsx
    │   │   ├── Watchlist.jsx
    │   │   ├── RecommendedStocks.jsx
    │   │   └── StockDetailModal.jsx
    │   ├── App.jsx
    │   └── main.jsx
    └── package.json
```

## 注意事项

- akshare数据源免费但可能有频率限制，建议合理设置缓存
- 人气榜数据来自东方财富，仅在交易时段有效
- 技术指标仅供参考，不构成投资建议
