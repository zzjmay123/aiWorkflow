"""
技术指标计算服务
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicator:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: List[int] = [5, 10, 20, 60, 120, 250]) -> pd.DataFrame:
        """计算移动平均线"""
        for period in periods:
            df[f'MA{period}'] = df['收盘'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """计算MACD指标"""
        ema_fast = df['收盘'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['收盘'].ewm(span=slow, adjust=False).mean()
        df['DIF'] = ema_fast - ema_slow
        df['DEA'] = df['DIF'].ewm(span=signal, adjust=False).mean()
        df['MACD'] = 2 * (df['DIF'] - df['DEA'])
        return df
    
    @staticmethod
    def calculate_kdj(df: pd.DataFrame, n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """计算KDJ指标"""
        low_min = df['最低'].rolling(window=n).min()
        high_max = df['最高'].rolling(window=n).max()
        
        rsv = (df['收盘'] - low_min) / (high_max - low_min) * 100
        rsv = rsv.fillna(50)
        
        df['K'] = rsv.ewm(com=m1-1, adjust=False).mean()
        df['D'] = df['K'].ewm(com=m2-1, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        return df
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> pd.DataFrame:
        """计算RSI指标"""
        for period in periods:
            delta = df['收盘'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            df[f'RSI{period}'] = 100 - (100 / (1 + rs))
        return df
    
    @staticmethod
    def calculate_boll(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """计算布林带"""
        df['BOLL_MID'] = df['收盘'].rolling(window=period).mean()
        std = df['收盘'].rolling(window=period).std()
        df['BOLL_UPPER'] = df['BOLL_MID'] + (std * std_dev)
        df['BOLL_LOWER'] = df['BOLL_MID'] - (std * std_dev)
        return df
    
    @staticmethod
    def calculate_volume_ratio(df: pd.DataFrame, short_period: int = 3, long_period: int = 5) -> pd.DataFrame:
        """
        计算成交量比率
        近N天平均成交量 / 前M天平均成交量
        """
        df['volume_ma_short'] = df['成交量'].rolling(window=short_period).mean()
        df['volume_ma_long'] = df['成交量'].rolling(window=long_period).mean().shift(short_period)
        df['volume_ratio'] = df['volume_ma_short'] / df['volume_ma_long']
        return df
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        df = TechnicalIndicator.calculate_ma(df)
        df = TechnicalIndicator.calculate_macd(df)
        df = TechnicalIndicator.calculate_kdj(df)
        df = TechnicalIndicator.calculate_rsi(df)
        df = TechnicalIndicator.calculate_boll(df)
        df = TechnicalIndicator.calculate_volume_ratio(df)
        return df
    
    @staticmethod
    def get_latest_indicators(df: pd.DataFrame) -> Dict:
        """获取最新一天的技术指标"""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        indicators = {
            'price': latest.get('收盘', 0),
            'change_pct': latest.get('涨跌幅', 0),
            'volume': latest.get('成交量', 0),
            'turnover': latest.get('成交额', 0),
            'ma': {
                'MA5': latest.get('MA5', 0),
                'MA10': latest.get('MA10', 0),
                'MA20': latest.get('MA20', 0),
                'MA60': latest.get('MA60', 0),
            },
            'macd': {
                'DIF': latest.get('DIF', 0),
                'DEA': latest.get('DEA', 0),
                'MACD': latest.get('MACD', 0),
            },
            'kdj': {
                'K': latest.get('K', 0),
                'D': latest.get('D', 0),
                'J': latest.get('J', 0),
            },
            'rsi': {
                'RSI6': latest.get('RSI6', 0),
                'RSI12': latest.get('RSI12', 0),
                'RSI24': latest.get('RSI24', 0),
            },
            'boll': {
                'UPPER': latest.get('BOLL_UPPER', 0),
                'MID': latest.get('BOLL_MID', 0),
                'LOWER': latest.get('BOLL_LOWER', 0),
            },
            'volume_ratio': latest.get('volume_ratio', 0),
        }
        
        # 判断趋势状态
        indicators['trend'] = TechnicalIndicator._analyze_trend(df)
        indicators['signals'] = TechnicalIndicator._generate_signals(df)
        
        return indicators
    
    @staticmethod
    def _analyze_trend(df: pd.DataFrame) -> Dict:
        """分析趋势状态"""
        if len(df) < 20:
            return {'status': 'unknown', 'description': '数据不足'}
        
        latest = df.iloc[-1]
        price = latest.get('收盘', 0)
        
        # 均线多头排列判断
        ma5 = latest.get('MA5', 0)
        ma10 = latest.get('MA10', 0)
        ma20 = latest.get('MA20', 0)
        ma60 = latest.get('MA60', 0)
        
        is_bullish = ma5 > ma10 > ma20
        is_bearish = ma5 < ma10 < ma20
        
        # 价格位置
        if price > ma5 > ma10 > ma20:
            trend_status = 'strong_uptrend'
            description = '强势上升'
        elif price > ma20 and ma5 > ma10:
            trend_status = 'uptrend'
            description = '上升趋势'
        elif price < ma5 < ma10 < ma20:
            trend_status = 'strong_downtrend'
            description = '强势下跌'
        elif price < ma20 and ma5 < ma10:
            trend_status = 'downtrend'
            description = '下跌趋势'
        else:
            trend_status = 'sideways'
            description = '震荡整理'
        
        return {
            'status': trend_status,
            'description': description,
            'is_bullish': is_bullish,
            'is_bearish': is_bearish,
            'price_vs_ma20': 'above' if price > ma20 else 'below',
        }
    
    @staticmethod
    def _generate_signals(df: pd.DataFrame) -> List[Dict]:
        """生成交易信号"""
        signals = []
        if len(df) < 2:
            return signals
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # MACD金叉/死叉
        if prev.get('DIF', 0) < prev.get('DEA', 0) and latest.get('DIF', 0) > latest.get('DEA', 0):
            signals.append({'type': 'buy', 'indicator': 'MACD', 'message': 'MACD金叉'})
        elif prev.get('DIF', 0) > prev.get('DEA', 0) and latest.get('DIF', 0) < latest.get('DEA', 0):
            signals.append({'type': 'sell', 'indicator': 'MACD', 'message': 'MACD死叉'})
        
        # KDJ金叉/死叉
        if prev.get('K', 50) < prev.get('D', 50) and latest.get('K', 50) > latest.get('D', 50):
            if latest.get('K', 50) < 30:
                signals.append({'type': 'buy', 'indicator': 'KDJ', 'message': 'KDJ低位金叉'})
        elif prev.get('K', 50) > prev.get('D', 50) and latest.get('K', 50) < latest.get('D', 50):
            if latest.get('K', 50) > 70:
                signals.append({'type': 'sell', 'indicator': 'KDJ', 'message': 'KDJ高位死叉'})
        
        # 放量信号
        volume_ratio = latest.get('volume_ratio', 0)
        if volume_ratio >= 3:
            signals.append({'type': 'info', 'indicator': 'Volume', 'message': f'放量{volume_ratio:.1f}倍'})
        
        return signals


# 全局实例
indicator_calculator = TechnicalIndicator()
