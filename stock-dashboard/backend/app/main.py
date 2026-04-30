"""
股票大盘展示系统 - 后端服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.routes import router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建FastAPI应用
app = FastAPI(
    title="股票大盘展示系统",
    description="A股技术面分析 + 人气指标推荐",
    version="1.0.0"
)

# 配置CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "股票大盘展示系统 API",
        "version": "1.0.0",
        "endpoints": {
            "市场概览": "/api/market/overview",
            "主要指数": "/api/indices",
            "人气推荐": "/api/popularity/recommended",
            "股票详情": "/api/stock/{symbol}",
            "搜索股票": "/api/stock/search?keyword=xxx",
            "关注列表": "/api/watchlist?symbols=000001,600000",
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
