import { useState, useEffect } from 'react';
import { Modal, Spin, Tabs, Row, Col, Card, Statistic, Tag, Descriptions } from 'antd';
import ReactECharts from 'echarts-for-react';
import { getStockDetail } from '../api';

function StockDetailModal({ visible, symbol, onClose }) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  useEffect(() => {
    if (visible && symbol) {
      fetchData();
    }
  }, [visible, symbol]);

  const fetchData = async () => {
    if (!symbol) return;
    try {
      setLoading(true);
      const res = await getStockDetail(symbol);
      if (res.data.success) {
        setData(res.data.data);
      }
    } catch (error) {
      console.error('获取股票详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const getKlineOption = () => {
    if (!data?.kline_data) return {};

    const klineData = data.kline_data;
    const dates = klineData.map(d => d.date);
    const ohlc = klineData.map(d => [d.open, d.close, d.low, d.high]);
    const volumes = klineData.map(d => d.volume);
    const ma5 = klineData.map(d => d.ma5);
    const ma10 = klineData.map(d => d.ma10);
    const ma20 = klineData.map(d => d.ma20);

    return {
      animation: false,
      legend: {
        data: ['K线', 'MA5', 'MA10', 'MA20'],
        top: 10,
      },
      grid: [
        { left: 60, right: 40, top: 50, height: '50%' },
        { left: 60, right: 40, top: '70%', height: '20%' },
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          gridIndex: 0,
          axisLabel: { show: false },
        },
        {
          type: 'category',
          data: dates,
          gridIndex: 1,
        },
      ],
      yAxis: [
        {
          scale: true,
          gridIndex: 0,
          splitArea: { show: true },
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
        },
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 50,
          end: 100,
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          top: '92%',
          start: 50,
          end: 100,
        },
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: ohlc,
          itemStyle: {
            color: '#f5222d',
            color0: '#52c41a',
            borderColor: '#f5222d',
            borderColor0: '#52c41a',
          },
        },
        {
          name: 'MA5',
          type: 'line',
          data: ma5,
          smooth: true,
          lineStyle: { width: 1 },
          symbol: 'none',
        },
        {
          name: 'MA10',
          type: 'line',
          data: ma10,
          smooth: true,
          lineStyle: { width: 1 },
          symbol: 'none',
        },
        {
          name: 'MA20',
          type: 'line',
          data: ma20,
          smooth: true,
          lineStyle: { width: 1 },
          symbol: 'none',
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumes.map((v, i) => ({
            value: v,
            itemStyle: {
              color: klineData[i].close >= klineData[i].open ? '#f5222d' : '#52c41a',
            },
          })),
        },
      ],
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        formatter: function (params) {
          if (!params.length) return '';
          const date = params[0].axisValue;
          let res = `<b>${date}</b><br/>`;
          params.forEach(p => {
            if (p.seriesName === 'K线' && p.value) {
              res += `开: ${p.value[1]}  收: ${p.value[2]}  低: ${p.value[3]}  高: ${p.value[4]}<br/>`;
            } else if (p.seriesName === '成交量') {
              res += `成交量: ${(p.value / 10000).toFixed(0)}万<br/>`;
            } else if (p.value !== null && p.value !== undefined) {
              res += `${p.seriesName}: ${p.value.toFixed(2)}<br/>`;
            }
          });
          return res;
        },
      },
    };
  };

  const getMACDOption = () => {
    if (!data?.kline_data) return {};

    const klineData = data.kline_data;
    const dates = klineData.map(d => d.date);
    const dif = klineData.map(d => d.macd?.dif);
    const dea = klineData.map(d => d.macd?.dea);
    const hist = klineData.map(d => d.macd?.hist);

    return {
      animation: false,
      title: { text: 'MACD', left: 'center', top: 5, textStyle: { fontSize: 14 } },
      legend: { data: ['DIF', 'DEA', 'MACD'], top: 25 },
      grid: { left: 60, right: 40, top: 50, bottom: 30 },
      xAxis: { type: 'category', data: dates },
      yAxis: { scale: true, splitArea: { show: true } },
      dataZoom: [{ type: 'inside', start: 50, end: 100 }],
      series: [
        {
          name: 'DIF',
          type: 'line',
          data: dif,
          lineStyle: { width: 1 },
          symbol: 'none',
        },
        {
          name: 'DEA',
          type: 'line',
          data: dea,
          lineStyle: { width: 1 },
          symbol: 'none',
        },
        {
          name: 'MACD',
          type: 'bar',
          data: hist.map((v, i) => ({
            value: v,
            itemStyle: { color: v >= 0 ? '#f5222d' : '#52c41a' },
          })),
        },
      ],
      tooltip: { trigger: 'axis' },
    };
  };

  const getKDJOption = () => {
    if (!data?.kline_data) return {};

    const klineData = data.kline_data;
    const dates = klineData.map(d => d.date);
    const k = klineData.map(d => d.kdj?.k);
    const d = klineData.map(d => d.kdj?.d);
    const j = klineData.map(d => d.kdj?.j);

    return {
      animation: false,
      title: { text: 'KDJ', left: 'center', top: 5, textStyle: { fontSize: 14 } },
      legend: { data: ['K', 'D', 'J'], top: 25 },
      grid: { left: 60, right: 40, top: 50, bottom: 30 },
      xAxis: { type: 'category', data: dates },
      yAxis: { min: 0, max: 100, splitArea: { show: true } },
      dataZoom: [{ type: 'inside', start: 50, end: 100 }],
      series: [
        { name: 'K', type: 'line', data: k, lineStyle: { width: 1 }, symbol: 'none' },
        { name: 'D', type: 'line', data: d, lineStyle: { width: 1 }, symbol: 'none' },
        { name: 'J', type: 'line', data: j, lineStyle: { width: 1 }, symbol: 'none' },
      ],
      tooltip: { trigger: 'axis' },
    };
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
    if (!signals || signals.length === 0) return <Tag>无信号</Tag>;
    return signals.map((s, i) => (
      <Tag key={i} color={s.type === 'buy' ? 'green' : s.type === 'sell' ? 'red' : 'blue'}>
        {s.message}
      </Tag>
    ));
  };

  const tabItems = [
    {
      key: 'kline',
      label: 'K线图',
      children: (
        <div>
          <ReactECharts option={getKlineOption()} style={{ height: 500 }} />
        </div>
      ),
    },
    {
      key: 'macd',
      label: 'MACD',
      children: <ReactECharts option={getMACDOption()} style={{ height: 300 }} />,
    },
    {
      key: 'kdj',
      label: 'KDJ',
      children: <ReactECharts option={getKDJOption()} style={{ height: 300 }} />,
    },
  ];

  return (
    <Modal
      title={`股票详情 - ${symbol}`}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={1000}
    >
      <Spin spinning={loading}>
        {data && (
          <div>
            {/* 基本信息 */}
            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="最新价"
                    value={data.latest_indicators?.price}
                    precision={2}
                    valueStyle={{ color: data.latest_indicators?.change_pct > 0 ? '#f5222d' : '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic
                    title="涨跌幅"
                    value={data.latest_indicators?.change_pct}
                    suffix="%"
                    precision={2}
                    valueStyle={{ color: data.latest_indicators?.change_pct > 0 ? '#f5222d' : '#52c41a' }}
                  />
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic title="趋势" value={null} />
                  <div style={{ marginTop: 8 }}>
                    {getTrendTag(data.latest_indicators?.trend)}
                  </div>
                </Card>
              </Col>
              <Col span={6}>
                <Card>
                  <Statistic title="信号" value={null} />
                  <div style={{ marginTop: 8 }}>
                    {getSignalTags(data.latest_indicators?.signals)}
                  </div>
                </Card>
              </Col>
            </Row>

            {/* 技术指标详情 */}
            <Card title="技术指标" style={{ marginBottom: 16 }}>
              <Descriptions column={4} size="small">
                <Descriptions.Item label="MA5">{data.latest_indicators?.ma?.MA5?.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="MA10">{data.latest_indicators?.ma?.MA10?.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="MA20">{data.latest_indicators?.ma?.MA20?.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="MA60">{data.latest_indicators?.ma?.MA60?.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="DIF">{data.latest_indicators?.macd?.DIF?.toFixed(3)}</Descriptions.Item>
                <Descriptions.Item label="DEA">{data.latest_indicators?.macd?.DEA?.toFixed(3)}</Descriptions.Item>
                <Descriptions.Item label="MACD">{data.latest_indicators?.macd?.MACD?.toFixed(3)}</Descriptions.Item>
                <Descriptions.Item label="放量倍数">{data.latest_indicators?.volume_ratio?.toFixed(1)}x</Descriptions.Item>
                <Descriptions.Item label="K">{data.latest_indicators?.kdj?.K?.toFixed(1)}</Descriptions.Item>
                <Descriptions.Item label="D">{data.latest_indicators?.kdj?.D?.toFixed(1)}</Descriptions.Item>
                <Descriptions.Item label="J">{data.latest_indicators?.kdj?.J?.toFixed(1)}</Descriptions.Item>
                <Descriptions.Item label="RSI6">{data.latest_indicators?.rsi?.RSI6?.toFixed(1)}</Descriptions.Item>
                <Descriptions.Item label="BOLL上轨">{data.latest_indicators?.boll?.UPPER?.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="BOLL中轨">{data.latest_indicators?.boll?.MID?.toFixed(2)}</Descriptions.Item>
                <Descriptions.Item label="BOLL下轨">{data.latest_indicators?.boll?.LOWER?.toFixed(2)}</Descriptions.Item>
              </Descriptions>
            </Card>

            {/* 图表 */}
            <Tabs items={tabItems} defaultActiveKey="kline" />
          </div>
        )}
      </Spin>
    </Modal>
  );
}

export default StockDetailModal;
