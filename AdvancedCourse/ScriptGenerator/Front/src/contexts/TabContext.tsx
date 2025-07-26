// contexts/TabContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';
import MainPage from '../pages/MainPage';
import DataStreamVM from '../pages/DataStreamVM';
import TrafficGeneratorVM from '../pages/TrafficGeneratorVM';
import ApiServerVM from '../pages/ApiServerVM';
import S3SinkConnectorVM from '../pages/S3SinkConnectorVM';
import HadoopSetting from '../pages/HadoopSetting';

interface Tab {
    id: string;
    label: string;
    content: React.ReactElement;
}

interface TabContextType {
    tabs: Tab[];
    activeTab: string;
    setActiveTab: (tabId: string) => void;
}

const TabContext = createContext<TabContextType | undefined>(undefined);

export const useTab = () => {
    const context = useContext(TabContext);
    if (!context) {
        throw new Error('useTab은 TabProvider 내부에서 사용해야 합니다');
    }
    return context;
};

export const TabProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [activeTab, setActiveTab] = useState('bastion-vm');
    
    const tabs: Tab[] = [
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
        <TabContext.Provider value={{ tabs, activeTab, setActiveTab }}>
            {children}
        </TabContext.Provider>
    );
};
