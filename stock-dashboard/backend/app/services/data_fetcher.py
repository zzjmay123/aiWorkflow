"""
数据获取服务 - 使用akshare获取A股数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """A股数据获取服务"""
    
    def __init__(self):
        self._cache = {}
        self._cache_time = {}
        self._cache_duration = 300  # 5分钟缓存
    
    def _get_cache(self, key: str) -> Optional[pd.DataFrame]:
        """获取缓存数据"""
        if key in self._cache:
            if (datetime.now() - self._cache_time[key]).seconds < self._cache_duration:
                return self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: pd.DataFrame):
        """设置缓存数据"""
        self._cache[key] = data
        self._cache_time[key] = datetime.now()
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取A股股票列表"""
        cache_key = "stock_list"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 获取沪深A股列表
            df = ak.stock_info_a_code_name()
            df.columns = ["code", "name"]
            self._set_cache(cache_key, df)
            return df
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return pd.DataFrame()
    
    def get_stock_history(self, symbol: str, period: str = "daily", 
                         start_date: str = None, end_date: str = None,
                         adjust: str = "qfq") -> pd.DataFrame:
        """
        获取股票历史行情数据
        
        Args:
            symbol: 股票代码
            period: 周期 (daily/weekly/monthly)
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            adjust: 复权类型 (qfq-前复权, hfq-后复权, 空字符串-不复权)
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        cache_key = f"history_{symbol}_{period}_{start_date}_{end_date}_{adjust}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            self._set_cache(cache_key, df)
            return df
        except Exception as e:
            logger.error(f"获取{symbol}历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_realtime(self) -> pd.DataFrame:
        """获取A股实时行情"""
        cache_key = "realtime"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = ak.stock_zh_a_spot_em()
            self._set_cache(cache_key, df)
            return df
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return pd.DataFrame()
    
    def get_index_history(self, symbol: str = "000001", 
                         start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取指数历史数据
        
        Args:
            symbol: 指数代码 (000001-上证指数, 399001-深证成指, 399006-创业板指)
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        cache_key = f"index_{symbol}_{start_date}_{end_date}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = ak.stock_zh_index_daily_em(
                symbol=f"sh{symbol}" if symbol.startswith("0") else f"sz{symbol}"
            )
            # 过滤日期范围
            df["date"] = pd.to_datetime(df["date"])
            df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
            self._set_cache(cache_key, df)
            return df
        except Exception as e:
            logger.error(f"获取指数{symbol}历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_popularity_rank(self, top_n: int = 200) -> pd.DataFrame:
        """
        获取东方财富人气排行榜
        
        Args:
            top_n: 返回前N名
        """
        cache_key = f"popularity_{top_n}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = ak.stock_hot_rank_em()
            df = df.head(top_n)
            self._set_cache(cache_key, df)
            return df
        except Exception as e:
            logger.error(f"获取人气排行榜失败: {e}")
            return pd.DataFrame()
    
    def get_index_realtime(self) -> Dict:
        """获取主要指数实时数据"""
        try:
            df = ak.stock_zh_index_spot_em()
            # 筛选主要指数
            main_indices = ["上证指数", "深证成指", "创业板指", "科创50", "沪深300"]
            result = df[df["名称"].isin(main_indices)]
            return result.to_dict("records")
        except Exception as e:
            logger.error(f"获取指数实时数据失败: {e}")
            return []


# 全局实例
data_fetcher = StockDataFetcher()
