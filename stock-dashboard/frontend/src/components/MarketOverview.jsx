import { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Table, Spin, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { getMarketOverview } from '../api';

function MarketOverview() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await getMarketOverview();
      if (res.data.success) {
        setData(res.data.data);
      }
    } catch (error) {
      console.error('获取市场概览失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  if (!data) {
    return <div>获取数据失败，请稍后重试</div>;
  }

  const upRatio = data.total > 0 ? ((data.up_count / data.total) * 100).toFixed(1) : 0;
  const downRatio = data.total > 0 ? ((data.down_count / data.total) * 100).toFixed(1) : 0;

  const topVolumeColumns = [
    { title: '代码', dataIndex: '代码', key: '代码', width: 80 },
    { title: '名称', dataIndex: '名称', key: '名称', width: 100 },
    {
      title: '最新价',
      dataIndex: '最新价',
      key: '最新价',
      render: (val) => val?.toFixed(2),
    },
    {
      title: '涨跌幅',
      dataIndex: '涨跌幅',
      key: '涨跌幅',
      render: (val) => (
        <span className={val > 0 ? 'text-up' : val < 0 ? 'text-down' : ''}>
          {val?.toFixed(2)}%
        </span>
      ),
    },
    {
      title: '成交额',
      dataIndex: '成交额',
      key: '成交额',
      render: (val) => {
        if (val > 1e8) return `${(val / 1e8).toFixed(2)}亿`;
        if (val > 1e4) return `${(val / 1e4).toFixed(2)}万`;
        return val;
      },
    },
  ];

  return (
    <div>
      {/* 市场情绪 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <div className="stat-card">
            <div className="label">上涨家数</div>
            <div className="value text-up">{data.up_count}</div>
            <div className="label">占比 {upRatio}%</div>
          </div>
        </Col>
        <Col span={6}>
          <div className="stat-card">
            <div className="label">下跌家数</div>
            <div className="value text-down">{data.down_count}</div>
            <div className="label">占比 {downRatio}%</div>
          </div>
        </Col>
        <Col span={6}>
          <div className="stat-card">
            <div className="label">涨停</div>
            <div className="value text-up">{data.limit_up}</div>
            <div className="label">家</div>
          </div>
        </Col>
        <Col span={6}>
          <div className="stat-card">
            <div className="label">跌停</div>
            <div className="value text-down">{data.limit_down}</div>
            <div className="label">家</div>
          </div>
        </Col>
      </Row>

      {/* 市场温度计 */}
      <Card title="市场温度计" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col span={12}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ flex: 1 }}>
                <div style={{ marginBottom: 8 }}>上涨比例</div>
                <div style={{ height: 24, background: '#f0f0f0', borderRadius: 12, overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${upRatio}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, #ff4d4f, #f5222d)',
                      borderRadius: 12,
                      transition: 'width 0.5s',
                    }}
                  />
                </div>
              </div>
              <span className="text-up" style={{ fontSize: 20, fontWeight: 'bold' }}>{upRatio}%</span>
            </div>
          </Col>
          <Col span={12}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ flex: 1 }}>
                <div style={{ marginBottom: 8 }}>下跌比例</div>
                <div style={{ height: 24, background: '#f0f0f0', borderRadius: 12, overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${downRatio}%`,
                      height: '100%',
                      background: 'linear-gradient(90deg, #52c41a, #73d13d)',
                      borderRadius: 12,
                      transition: 'width 0.5s',
                    }}
                  />
                </div>
              </div>
              <span className="text-down" style={{ fontSize: 20, fontWeight: 'bold' }}>{downRatio}%</span>
            </div>
          </Col>
        </Row>
      </Card>

      {/* 成交额TOP10 */}
      <Card title="成交额 TOP10">
        <Table
          columns={topVolumeColumns}
          dataSource={data.top_volume || []}
          rowKey="代码"
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
}

export default MarketOverview;
