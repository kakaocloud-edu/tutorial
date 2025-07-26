import React from 'react';
import Tabs from './components/Tabs';
import MainPage from './pages/MainPage';
import DataStreamVM from './pages/DataStreamVM';
import TrafficGeneratorVM from './pages/TrafficGeneratorVM';
import ApiServerVM from './pages/ApiServerVM';
import S3SinkConnectorVM from './pages/S3SinkConnectorVM';
import HadoopSetting from './pages/HadoopSetting';
import GlobalStyle from './styles/GlobalStyle';
import { TabProvider } from './contexts/TabContext';

const App: React.FC = () => {
    const tabs = [
        {
            id: 'bastion-vm',
            label: 'Bastion VM 스크립트 생성',
            content: <MainPage />
        },
        {
            id: 'datastream-vm',
            label: 'DataStream VM 스크립트 생성',
            content: <DataStreamVM />
        },
        {
            id: 'traffic-vm',
            label: '트래픽 생성기 VM 스크립트 생성',
            content: <TrafficGeneratorVM />
        },
        {
            id: 'api-server-vm',
            label: 'API Server VM 스크립트 생성',
            content: <ApiServerVM />
        },
        {
            id: 's3-sink-connector-vm',
            label: 'S3 Sink Connector VM 스크립트 생성',
            content: <S3SinkConnectorVM />
        },
        {
            id: 'hadoop-setting',
            label: 'Hadoop Configuration 생성',
            content: <HadoopSetting />
        }
    ];

    return (
        <>
            <GlobalStyle />
            <TabProvider>
                <Tabs tabs={tabs} defaultTab="bastion-vm" />
            </TabProvider>
        </>
    );
};

export default App;
