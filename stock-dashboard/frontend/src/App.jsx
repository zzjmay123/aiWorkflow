import { useState } from 'react';
import { Layout, Menu, theme } from 'antd';
import { DashboardOutlined, StarOutlined, RocketOutlined } from '@ant-design/icons';
import MarketOverview from './components/MarketOverview';
import Watchlist from './components/Watchlist';
import RecommendedStocks from './components/RecommendedStocks';
import './App.css';

const { Header, Content, Sider } = Layout;

function App() {
  const [currentTab, setCurrentTab] = useState('market');
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const items = [
    {
      key: 'market',
      icon: <DashboardOutlined />,
      label: '大盘概览',
    },
    {
      key: 'watchlist',
      icon: <StarOutlined />,
      label: '我的关注',
    },
    {
      key: 'recommended',
      icon: <RocketOutlined />,
      label: '每日推荐',
    },
  ];

  const renderContent = () => {
    switch (currentTab) {
      case 'market':
        return <MarketOverview />;
      case 'watchlist':
        return <Watchlist />;
      case 'recommended':
        return <RecommendedStocks />;
      default:
        return <MarketOverview />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="80">
        <div className="logo">
          <h2 style={{ color: '#fff', textAlign: 'center', padding: '16px 0', margin: 0, fontSize: '18px' }}>
            股票大盘
          </h2>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[currentTab]}
          items={items}
          onClick={({ key }) => setCurrentTab(key)}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            padding: '0 24px',
            background: colorBgContainer,
            display: 'flex',
            alignItems: 'center',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <h1 style={{ margin: 0, fontSize: '20px' }}>
            {currentTab === 'market' && '大盘概览'}
            {currentTab === 'watchlist' && '我的关注'}
            {currentTab === 'recommended' && '每日推荐'}
          </h1>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
