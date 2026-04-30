import { useState, useEffect } from 'react';
import { Table, Tag, Card, Spin, Input, Button, Space, Modal } from 'antd';
import { SearchOutlined, StarOutlined, StarFilled } from '@ant-design/icons';
import { getWatchlist, getStockDetail } from '../api';
import StockDetailModal from './StockDetailModal';

// 默认关注的股票列表（可以自定义）
const DEFAULT_WATCHLIST = ['000001', '600000', '000002', '600519', '000858'];

function Watchlist() {
  const [loading, setLoading] = useState(true);
  const [stocks, setStocks] = useState([]);
  const [watchlistSymbols, setWatchlistSymbols] = useState(DEFAULT_WATCHLIST);
  const [searchValue, setSearchValue] = useState('');
  const [selectedStock, setSelectedStock] = useState(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      setLoading(true);
      const res = await getWatchlist(watchlistSymbols.join(','));
      if (res.data.success) {
        setStocks(res.data.data || []);
      }
    } catch (error) {
      console.error('获取关注列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = async (symbol) => {
    try {
      setDetailLoading(true);
      setSelectedStock(symbol);
      setDetailVisible(true);
    } finally {
      setDetailLoading(false);
    }
  };

  const getTrendTag = (trend) => {
    if (!trend) return null;
    const statusMap = {
      strong_uptrend: { color: 'green', text: '强势上升' },
      uptrend: { color: 'lime', text: '上升趋势' },
      sideways: { color: 'orange', text: '震荡整理' },
      downtrend: { color: 'red', text: '下跌趋势' },
      strong_downtrend: { color: 'magenta', text: '强势下跌' },
    };
    const config = statusMap[trend.status] || { color: 'default', text: trend.description || '未知' };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getSignalTags = (signals) => {
    if (!signals || signals.length === 0) return '-';
    return signals.map((s, i) => (
      <Tag key={i} color={s.type === 'buy' ? 'green' : s.type === 'sell' ? 'red' : 'blue'}>
        {s.message}
      </Tag>
    ));
  };

  const columns = [
    {
      title: '代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 80,
      fixed: 'left',
    },
    {
      title: '最新价',
      dataIndex: ['latest', 'price'],
      key: 'price',
      width: 90,
      render: (val) => val?.toFixed(2),
    },
    {
      title: '涨跌幅',
      dataIndex: ['latest', 'change_pct'],
      key: 'change_pct',
      width: 90,
      render: (val) => (
        <span className={val > 0 ? 'text-up' : val < 0 ? 'text-down' : ''}>
          {val?.toFixed(2)}%
        </span>
      ),
    },
    {
      title: 'MA5',
      dataIndex: ['latest', 'ma', 'MA5'],
      key: 'MA5',
      width: 80,
      render: (val) => val?.toFixed(2),
    },
    {
      title: 'MA20',
      dataIndex: ['latest', 'ma', 'MA20'],
      key: 'MA20',
      width: 80,
      render: (val) => val?.toFixed(2),
    },
    {
      title: 'MACD',
      dataIndex: ['latest', 'macd'],
      key: 'macd',
      width: 100,
      render: (macd) => (
        <span className={macd?.DIF > macd?.DEA ? 'text-up' : 'text-down'}>
          {macd?.DIF?.toFixed(2)} / {macd?.DEA?.toFixed(2)}
        </span>
      ),
    },
    {
      title: 'KDJ',
      dataIndex: ['latest', 'kdj'],
      key: 'kdj',
      width: 100,
      render: (kdj) => `${kdj?.K?.toFixed(1)} / ${kdj?.D?.toFixed(1)} / ${kdj?.J?.toFixed(1)}`,
    },
    {
      title: 'RSI6',
      dataIndex: ['latest', 'rsi', 'RSI6'],
      key: 'RSI6',
      width: 70,
      render: (val) => val?.toFixed(1),
    },
    {
      title: '放量倍数',
      dataIndex: ['latest', 'volume_ratio'],
      key: 'volume_ratio',
      width: 90,
      render: (val) => (
        <span className={val >= 3 ? 'text-up' : ''}>
          {val?.toFixed(1)}x
        </span>
      ),
    },
    {
      title: '趋势',
      dataIndex: ['latest', 'trend'],
      key: 'trend',
      width: 100,
      render: getTrendTag,
    },
    {
      title: '信号',
      dataIndex: ['latest', 'signals'],
      key: 'signals',
      width: 150,
      render: getSignalTags,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Button type="link" onClick={() => handleViewDetail(record.symbol)}>
          详情
        </Button>
      ),
    },
  ];

  const filteredStocks = stocks.filter(s => 
    s.symbol.includes(searchValue)
  );

  return (
    <div>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索股票代码"
            prefix={<SearchOutlined />}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            style={{ width: 200 }}
          />
          <Button type="primary" onClick={fetchWatchlist} loading={loading}>
            刷新
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={filteredStocks}
          rowKey="symbol"
          loading={loading}
          pagination={false}
          scroll={{ x: 1200 }}
          size="small"
        />
      </Card>

      <StockDetailModal
        visible={detailVisible}
        symbol={selectedStock}
        onClose={() => setDetailVisible(false)}
      />
    </div>
  );
}

export default Watchlist;
