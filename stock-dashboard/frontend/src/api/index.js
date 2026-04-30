import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// 获取主要指数
export const getIndices = () => api.get('/api/indices');

// 获取市场概览
export const getMarketOverview = () => api.get('/api/market/overview');

// 获取人气推荐股票
export const getPopularityRecommended = (topN = 200, minVolumeRatio = 3.0) => 
  api.get('/api/popularity/recommended', { 
    params: { top_n: topN, min_volume_ratio: minVolumeRatio } 
  });

// 获取股票详情
export const getStockDetail = (symbol, days = 120) => 
  api.get(`/api/stock/${symbol}`, { params: { days } });

// 搜索股票
export const searchStock = (keyword) => 
  api.get('/api/stock/search', { params: { keyword } });

// 获取关注列表
export const getWatchlist = (symbols) => 
  api.get('/api/watchlist', { params: { symbols } });

export default api;
