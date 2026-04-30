"""
REST API路由
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
import logging

from app.services import data_fetcher, popularity_screener

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["股票数据"])


@router.get("/indices")
async def get_indices():
    """获取主要指数实时数据"""
    try:
        indices = data_fetcher.get_index_realtime()
        return {"success": True, "data": indices}
    except Exception as e:
        logger.error(f"获取指数数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/overview")
async def get_market_overview():
    """获取市场概览（涨跌统计）"""
    try:
        realtime_df = data_fetcher.get_stock_realtime()
        if realtime_df.empty:
            return {"success": False, "message": "获取数据失败"}
        
        total = len(realtime_df)
        up_count = len(realtime_df[realtime_df['涨跌幅'] > 0])
        down_count = len(realtime_df[realtime_df['涨跌幅'] < 0])
        flat_count = total - up_count - down_count
        
        # 涨停跌停统计
        limit_up = len(realtime_df[realtime_df['涨跌幅'] >= 9.9])
        limit_down = len(realtime_df[realtime_df['涨跌幅'] <= -9.9])
        
        # 成交额TOP10
        top_volume = realtime_df.nlargest(10, '成交额')[['代码', '名称', '最新价', '涨跌幅', '成交额']].to_dict("records")
        
        return {
            "success": True,
            "data": {
                "total": total,
                "up_count": up_count,
                "down_count": down_count,
                "flat_count": flat_count,
                "limit_up": limit_up,
                "limit_down": limit_down,
                "top_volume": top_volume,
            }
        }
    except Exception as e:
        logger.error(f"获取市场概览失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/popularity/recommended")
async def get_popularity_recommended(top_n: int = 200, min_volume_ratio: float = 3.0):
    """
    获取人气推荐股票
    筛选条件：人气前200 + 上升趋势 + 放量3倍
    """
    try:
        stocks = popularity_screener.screen_popular_stocks(
            top_n=top_n,
            min_volume_ratio=min_volume_ratio
        )
        return {"success": True, "data": stocks, "count": len(stocks)}
    except Exception as e:
        logger.error(f"获取人气推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/{symbol}")
async def get_stock_detail(symbol: str, days: int = 120):
    """获取单只股票详细数据和技术指标"""
    try:
        detail = popularity_screener.get_stock_detail(symbol=symbol, days=days)
        if 'error' in detail:
            raise HTTPException(status_code=404, detail=detail['error'])
        return {"success": True, "data": detail}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票{symbol}详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock/search")
async def search_stock(keyword: str):
    """搜索股票"""
    try:
        stock_list = data_fetcher.get_stock_list()
        if stock_list.empty:
            return {"success": True, "data": []}
        
        # 按代码或名称搜索
        results = stock_list[
            stock_list['code'].str.contains(keyword) | 
            stock_list['name'].str.contains(keyword)
        ].head(20)
        
        return {"success": True, "data": results.to_dict("records")}
    except Exception as e:
        logger.error(f"搜索股票失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist")
async def get_watchlist(symbols: str = None):
    """
    获取关注股票列表的技术指标
    symbols: 逗号分隔的股票代码，如 "000001,600000,000002"
    """
    try:
        if not symbols:
            return {"success": True, "data": []}
        
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        results = []
        
        for symbol in symbol_list:
            try:
                detail = popularity_screener.get_stock_detail(symbol=symbol, days=60)
                if 'error' not in detail:
                    results.append({
                        'symbol': symbol,
                        'latest': detail.get('latest_indicators', {}),
                    })
            except Exception as e:
                logger.error(f"获取{symbol}失败: {e}")
                continue
        
        return {"success": True, "data": results}
    except Exception as e:
        logger.error(f"获取关注列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
