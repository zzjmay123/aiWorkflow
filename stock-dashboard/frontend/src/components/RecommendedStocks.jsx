import { useState, useEffect } from 'react';
import { Table, Tag, Card, Spin, Space, Button, Statistic, Row, Col } from 'antd';
import { ReloadOutlined, TrophyOutlined, FireOutlined, RiseOutlined } from '@ant-design/icons';
import { getPopularityRecommended } from '../api';
import StockDetailModal from './StockDetailModal';

function RecommendedStocks() {
  const [loading, setLoading] = useState(true);
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [detailVisible, setDetailVisible] = useState(false);

  useEffect(() => {
    fetchRecommended();
  }, []);

  const fetchRecommended = async () => {
    try {
      setLoading(true);
      const res = await getPopularityRecommended(200, 3.0);
      if (res.data.success) {
        setStocks(res.data.data || []);
      }
    } catch (error) {
      console.error('获取推荐股票失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetail = (symbol) => {
    setSelectedStock(symbol);
    setDetailVisible(true);
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

  const getScoreColor = (score) => {
    if (score >= 80) return '#f5222d';
    if (score >= 60) return '#fa8c16';
    if (score >= 40) return '#faad14';
    return '#8c8c8c';
  };

  const columns = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 70,
      render: (rank) => (
        <span>
          {rank <= 3 ? (
            <TrophyOutlined style={{ color: rank === 1 ? '#ffd700' : rank === 2 ? '#c0c0c0' : '#cd7f32' }} />
          ) : null}
          {rank}
        </span>
      ),
    },
    {
      title: '代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 80,
      fixed: 'left',
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 100,
      fixed: 'left',
    },
    {
      title: '最新价',
      dataIndex: 'price',
      key: 'price',
      width: 90,
      render: (val) => val?.toFixed(2),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
      width: 90,
      render: (val) => (
        <span className={val > 0 ? 'text-up' : val < 0 ? 'text-down' : ''}>
          {val?.toFixed(2)}%
        </span>
      ),
    },
    {
      title: (
        <span>
          <FireOutlined style={{ color: '#f5222d' }} /> 放量倍数
        </span>
      ),
      dataIndex: 'volume_ratio',
      key: 'volume_ratio',
      width: 100,
      sorter: (a, b) => a.volume_ratio - b.volume_ratio,
      defaultSortOrder: 'descend',
      render: (val) => (
        <Tag color={val >= 5 ? 'red' : val >= 3 ? 'orange' : 'default'}>
          {val?.toFixed(1)}x
        </Tag>
      ),
    },
    {
      title: '趋势',
      dataIndex: 'trend',
      key: 'trend',
      width: 100,
      render: getTrendTag,
    },
    {
      title: 'MACD',
      dataIndex: ['indicators', 'macd'],
      key: 'macd',
      width: 100,
      render: (macd) => (
        <span className={macd?.DIF > macd?.DEA ? 'text-up' : 'text-down'}>
          DIF {macd?.DIF?.toFixed(2)}
        </span>
      ),
    },
    {
      title: 'KDJ',
      dataIndex: ['indicators', 'kdj'],
      key: 'kdj',
      width: 100,
      render: (kdj) => `K:${kdj?.K?.toFixed(0)} D:${kdj?.D?.toFixed(0)}`,
    },
    {
      title: '信号',
      dataIndex: 'signals',
      key: 'signals',
      width: 150,
      render: getSignalTags,
    },
    {
      title: (
        <span>
          <RiseOutlined /> 评分
        </span>
      ),
      dataIndex: 'score',
      key: 'score',
      width: 80,
      sorter: (a, b) => a.score - b.score,
      render: (score) => (
        <span style={{ color: getScoreColor(score), fontWeight: 'bold', fontSize: 16 }}>
          {score}
        </span>
      ),
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

  return (
    <div>
      {/* 筛选条件说明 */}
      <Card style={{ marginBottom: 16, background: '#fffbe6' }}>
        <Space>
          <FireOutlined style={{ color: '#f5222d', fontSize: 20 }} />
          <span>
            <strong>筛选条件：</strong>
            人气榜前200名 + 上升趋势 + 近3天成交量是前5天的3倍以上
          </span>
        </Space>
      </Card>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="推荐股票数"
              value={stocks.length}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均放量倍数"
              value={stocks.length > 0 ? (stocks.reduce((sum, s) => sum + s.volume_ratio, 0) / stocks.length).toFixed(1) : 0}
              suffix="x"
              precision={1}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="上升趋势"
              value={stocks.filter(s => s.trend?.status?.includes('uptrend')).length}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="买入信号"
              value={stocks.filter(s => s.signals?.some(sig => sig.type === 'buy')).length}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 股票列表 */}
      <Card
        title="每日推荐股票"
        extra={
          <Button type="primary" icon={<ReloadOutlined />} onClick={fetchRecommended} loading={loading}>
            刷新
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={stocks}
          rowKey="symbol"
          loading={loading}
          pagination={{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `共 ${total} 只` }}
          scroll={{ x: 1300 }}
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

export default RecommendedStocks;
