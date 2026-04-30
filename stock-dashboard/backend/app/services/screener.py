"""
人气指标筛选服务
筛选条件：
1. 东方财富人气榜前200名
2. 上升趋势（均线多头排列或价格在MA20上方）
3. 近3天交易量是前5个交易日成交量的3倍
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from app.services.data_fetcher import data_fetcher
from app.services.indicator import indicator_calculator

logger = logging.getLogger(__name__)


class PopularityScreener:
    """人气指标筛选器"""
    
    def __init__(self):
        self.data_fetcher = data_fetcher
        self.indicator_calculator = indicator_calculator
    
    def screen_popular_stocks(self, top_n: int = 200, min_volume_ratio: float = 3.0) -> List[Dict]:
        """
        筛选人气股票
        
        Args:
            top_n: 人气榜前N名
            min_volume_ratio: 最小放量倍数（默认3倍）
        
        Returns:
            符合条件的股票列表
        """
        # 1. 获取人气排行榜
        popularity_df = self.data_fetcher.get_popularity_rank(top_n=top_n)
        if popularity_df.empty:
            logger.warning("获取人气排行榜失败")
            return []
        
        logger.info(f"获取到人气榜前{len(popularity_df)}名股票")
        
        # 2. 逐个分析股票
        qualified_stocks = []
        
        for idx, row in popularity_df.iterrows():
            try:
                symbol = row.get('代码', '')
                name = row.get('名称', '')
                rank = idx + 1
                
                if not symbol:
                    continue
                
                # 获取历史数据（需要足够天数计算指标）
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=180)).strftime("%Y%m%d")
                
                history_df = self.data_fetcher.get_stock_history(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if history_df.empty or len(history_df) < 30:
                    continue
                
                # 计算技术指标
                history_df = self.indicator_calculator.calculate_all_indicators(history_df)
                
                # 3. 检查上升趋势
                if not self._is_uptrend(history_df):
                    continue
                
                # 4. 检查放量条件
                volume_ratio = self._check_volume_surge(history_df, min_volume_ratio)
                if volume_ratio < min_volume_ratio:
                    continue
                
                # 获取最新指标
                latest_indicators = self.indicator_calculator.get_latest_indicators(history_df)
                
                # 符合条件，加入结果
                qualified_stocks.append({
                    'rank': rank,
                    'symbol': symbol,
                    'name': name,
                    'price': latest_indicators.get('price', 0),
                    'change_pct': latest_indicators.get('change_pct', 0),
                    'volume_ratio': round(volume_ratio, 2),
                    'trend': latest_indicators.get('trend', {}),
                    'signals': latest_indicators.get('signals', []),
                    'indicators': latest_indicators,
                    'score': self._calculate_score(latest_indicators, volume_ratio, rank),
                })
                
            except Exception as e:
                logger.error(f"分析股票{row.get('代码', '')}失败: {e}")
                continue
        
        # 按评分排序
        qualified_stocks.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"筛选完成，共{len(qualified_stocks)}只股票符合条件")
        return qualified_stocks
    
    def _is_uptrend(self, df: pd.DataFrame) -> bool:
        """
        判断是否为上升趋势
        
        条件（满足任一即可）：
        1. 均线多头排列：MA5 > MA10 > MA20
        2. 价格在MA20上方且MA20向上
        3. 近期创出新高（20日内）
        """
        if len(df) < 25:
            return False
        
        latest = df.iloc[-1]
        price = latest.get('收盘', 0)
        
        ma5 = latest.get('MA5', 0)
        ma10 = latest.get('MA10', 0)
        ma20 = latest.get('MA20', 0)
        ma60 = latest.get('MA60', 0)
        
        # 条件1：均线多头排列
        if ma5 > ma10 > ma20:
            return True
        
        # 条件2：价格在MA20上方且MA20向上
        if price > ma20 and ma20 > 0:
            # 检查MA20是否向上（当前MA20 > 5天前MA20）
            if len(df) >= 25:
                ma20_5days_ago = df.iloc[-5].get('MA20', 0)
                if ma20 > ma20_5days_ago:
                    return True
        
        # 条件3：近期创出20日新高
        recent_20 = df.tail(20)
        high_20 = recent_20['最高'].max()
        if price >= high_20 * 0.98:  # 接近新高也算
            return True
        
        return False
    
    def _check_volume_surge(self, df: pd.DataFrame, min_ratio: float = 3.0) -> float:
        """
        检查放量条件
        近3天平均成交量 / 前5天平均成交量 >= 3
        
        Returns:
            成交量比率，如果不符合返回0
        """
        if len(df) < 8:
            return 0
        
        # 近3天平均成交量
        recent_3_days = df.tail(3)['成交量'].mean()
        
        # 前5天平均成交量（近3天之前的5天）
        prev_5_days = df.iloc[-8:-3]['成交量'].mean()
        
        if prev_5_days == 0:
            return 0
        
        volume_ratio = recent_3_days / prev_5_days
        return volume_ratio
    
    def _calculate_score(self, indicators: Dict, volume_ratio: float, rank: int) -> float:
        """
        计算股票综合评分
        
        评分因素：
        - 人气排名（权重20%）
        - 放量倍数（权重30%）
        - 趋势强度（权重30%）
        - 技术指标信号（权重20%）
        """
        score = 0
        
        # 人气排名得分（排名越靠前分数越高）
        rank_score = max(0, 100 - rank * 0.5)
        score += rank_score * 0.2
        
        # 放量得分
        volume_score = min(100, volume_ratio * 20)
        score += volume_score * 0.3
        
        # 趋势得分
        trend = indicators.get('trend', {})
        trend_status = trend.get('status', '')
        if trend_status == 'strong_uptrend':
            trend_score = 100
        elif trend_status == 'uptrend':
            trend_score = 80
        elif trend_status == 'sideways':
            trend_score = 50
        else:
            trend_score = 20
        score += trend_score * 0.3
        
        # 信号得分
        signals = indicators.get('signals', [])
        buy_signals = len([s for s in signals if s.get('type') == 'buy'])
        signal_score = min(100, buy_signals * 50)
        score += signal_score * 0.2
        
        return round(score, 2)
    
    def get_stock_detail(self, symbol: str, days: int = 120) -> Dict:
        """
        获取单只股票的详细数据
        
        Args:
            symbol: 股票代码
            days: 获取天数
        
        Returns:
            股票详细数据
        """
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        # 获取历史数据
        history_df = self.data_fetcher.get_stock_history(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if history_df.empty:
            return {'error': '获取数据失败'}
        
        # 计算指标
        history_df = self.indicator_calculator.calculate_all_indicators(history_df)
        
        # 获取最新指标
        latest = self.indicator_calculator.get_latest_indicators(history_df)
        
        # 准备K线数据（用于前端图表）
        kline_data = []
        for _, row in history_df.iterrows():
            kline_data.append({
                'date': str(row.get('日期', '')),
                'open': float(row.get('开盘', 0)),
                'high': float(row.get('最高', 0)),
                'low': float(row.get('最低', 0)),
                'close': float(row.get('收盘', 0)),
                'volume': float(row.get('成交量', 0)),
                'ma5': float(row.get('MA5', 0)) if pd.notna(row.get('MA5')) else None,
                'ma10': float(row.get('MA10', 0)) if pd.notna(row.get('MA10')) else None,
                'ma20': float(row.get('MA20', 0)) if pd.notna(row.get('MA20')) else None,
                'macd': {
                    'dif': float(row.get('DIF', 0)) if pd.notna(row.get('DIF')) else None,
                    'dea': float(row.get('DEA', 0)) if pd.notna(row.get('DEA')) else None,
                    'hist': float(row.get('MACD', 0)) if pd.notna(row.get('MACD')) else None,
                },
                'kdj': {
                    'k': float(row.get('K', 0)) if pd.notna(row.get('K')) else None,
                    'd': float(row.get('D', 0)) if pd.notna(row.get('D')) else None,
                    'j': float(row.get('J', 0)) if pd.notna(row.get('J')) else None,
                },
            })
        
        return {
            'symbol': symbol,
            'kline_data': kline_data,
            'latest_indicators': latest,
            'history_summary': {
                'high_60d': float(history_df.tail(60)['最高'].max()),
                'low_60d': float(history_df.tail(60)['最低'].min()),
                'avg_volume_60d': float(history_df.tail(60)['成交量'].mean()),
            }
        }


# 全局实例
popularity_screener = PopularityScreener()
