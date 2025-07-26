import React, { useState } from 'react';
import styled, { keyframes, css } from 'styled-components';
import axios from 'axios';

// 기존 스타일 컴포넌트들은 동일 (spin, ToggleContainer, Label 등...)

const spin = keyframes`
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
`;

const ToggleContainer = styled.div`
    margin-bottom: 1em;
`;

const Label = styled.label`
    display: block;
    margin-bottom: 0.5em;
    color: #ffe100;
    font-size: 1em;
`;

const QuerySection = styled.div`
    display: flex;
    align-items: center;
    gap: 1em;
    padding: 1em;
    background: linear-gradient(135deg, rgba(255, 225, 0, 0.1) 0%, rgba(255, 225, 0, 0.05) 100%);
    border: 1px solid rgba(255, 225, 0, 0.2);
    border-radius: 8px;
    margin-bottom: 1em;
    transition: all 0.3s ease;
    
    &:hover {
        border-color: rgba(255, 225, 0, 0.4);
        background: linear-gradient(135deg, rgba(255, 225, 0, 0.15) 0%, rgba(255, 225, 0, 0.08) 100%);
    }
`;

const QueryText = styled.div`
    flex: 1;
    color: #fff;
    font-size: 0.95em;
`;

const QueryButton = styled.button<{ $isLoading: boolean }>`
    background: linear-gradient(135deg, #ffe100 0%, #ffec4f 100%);
    color: #000;
    border: none;
    padding: 0.6em 1.2em;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.85em;
    font-weight: 500;
    transition: all 0.2s ease;
    position: relative;
    min-width: 80px;
    
    &:hover:not(:disabled) {
        background: linear-gradient(135deg, #ffec4f 0%, #fff176 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(255, 225, 0, 0.3);
    }
    
    &:disabled {
        background: #666;
        cursor: not-allowed;
        transform: none;
    }
    
    ${props => props.$isLoading && css`
        &::after {
            content: '';
            position: absolute;
            width: 14px;
            height: 14px;
            margin: auto;
            border: 2px solid #000;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: ${spin} 1s linear infinite;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
    `}
`;

const LoadingText = styled.span<{ $visible: boolean }>`
    opacity: ${props => props.$visible ? 0 : 1};
    transition: opacity 0.2s ease;
`;

const ClusterList = styled.div`
    display: flex;
    flex-direction: column;
    gap: 0.5em;
    max-height: 250px;
    overflow-y: auto;
    padding: 0.5em;
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    
    &::-webkit-scrollbar {
        width: 6px;
    }
    
    &::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
    
    &::-webkit-scrollbar-thumb {
        background: rgba(255, 225, 0, 0.5);
        border-radius: 3px;
    }
    
    &::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 225, 0, 0.7);
    }
`;

const ClusterOption = styled.label<{ $selected: boolean }>`
    display: flex;
    align-items: center;
    padding: 1em;
    background: ${props => props.$selected 
        ? 'linear-gradient(135deg, rgba(255, 225, 0, 0.2) 0%, rgba(255, 225, 0, 0.1) 100%)'
        : 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.04) 100%)'
    };
    border: 1px solid ${props => props.$selected ? 'rgba(255, 225, 0, 0.5)' : 'rgba(255, 255, 255, 0.1)'};
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover {
        background: linear-gradient(135deg, rgba(255, 225, 0, 0.15) 0%, rgba(255, 225, 0, 0.08) 100%);
        border-color: rgba(255, 225, 0, 0.3);
        transform: translateY(-1px);
    }
`;

const RadioInput = styled.input`
    margin-right: 1em;
    width: 18px;
    height: 18px;
    accent-color: #ffe100;
    cursor: pointer;
`;

const ClusterInfo = styled.div`
    flex: 1;
    color: #fff;
`;

const ClusterName = styled.div`
    font-weight: bold;
    margin-bottom: 0.4em;
    font-size: 1em;
    display: flex;
    align-items: center;
`;

const ClusterDetails = styled.div`
    font-size: 0.85em;
    color: #ccc;
    line-height: 1.4;
`;

const StatusBadge = styled.span<{ $status: string }>`
    padding: 0.3em 0.7em;
    border-radius: 15px;
    font-size: 0.75em;
    background: ${props => props.$status === 'Active' 
        ? 'linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%)'
        : 'linear-gradient(135deg, #f44336 0%, #ef5350 100%)'
    };
    color: white;
    margin-left: 0.8em;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
`;

const EmptyState = styled.div`
    text-align: center;
    color: #999;
    padding: 2em 1em;
    font-style: italic;
`;

interface Cluster {
    id: string;
    name: string;
    status: string;
    version: string;
    bootstrap_servers: string;
    total_broker_count: number;
    instance_type: string;
}

// 수정된 인터페이스 - 기존과 새로운 방식 모두 지원
interface ClusterToggleProps {
    label: string;
    selectedClusterId: string;
    onClusterSelect: (clusterId: string, bootstrapServers: string) => void;
    
    // 기존 방식 (개별 조회) - 선택적
    accessKey?: string;
    secretKey?: string;
    
    // 새로운 방식 (통합 조회) - 선택적  
    clusters?: Cluster[];
    isLoaded?: boolean;
    hideButton?: boolean;
}

const ClusterToggle: React.FC<ClusterToggleProps> = ({
    label,
    selectedClusterId,
    onClusterSelect,
    accessKey = '',
    secretKey = '',
    clusters = [],
    isLoaded = false,
    hideButton = false
}) => {
    const [localClusters, setLocalClusters] = useState<Cluster[]>([]);
    const [localLoading, setLocalLoading] = useState(false);
    const [localLoaded, setLocalLoaded] = useState(false);

    // 기존 개별 조회 로직
    const fetchClusters = async () => {
        if (!accessKey || !secretKey) {
            alert('액세스 키와 시크릿 키를 먼저 입력해주세요.');
            return;
        }

        setLocalLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/get-kafka-clusters', {
                access_key_id: accessKey,
                access_key_secret: secretKey,
            });
            
            const clusterDetails = response.data.cluster_details || [];
            setLocalClusters(clusterDetails);
            setLocalLoaded(true);
            
            if (clusterDetails.length === 0) {
                alert('사용 가능한 Kafka 클러스터가 없습니다.');
            }
        } catch (error) {
            console.error('Kafka 클러스터 조회 오류:', error);
            alert('Kafka 클러스터 조회 중 오류가 발생했습니다.');
            setLocalClusters([]);
        }
        setLocalLoading(false);
    };

    const handleClusterChange = (clusterId: string, bootstrapServers: string) => {
        onClusterSelect(clusterId, bootstrapServers);
    };

    // 외부에서 전달받은 데이터가 있으면 그것을 우선 사용, 없으면 로컬 데이터 사용
    const displayClusters = clusters.length > 0 ? clusters : localClusters;
    const displayLoaded = isLoaded || localLoaded;
    const keysProvided = Boolean(accessKey && secretKey);

    return (
        <ToggleContainer>
            <Label>{label}</Label>
            
            {!hideButton && (
                <QuerySection>
                    <QueryText>
                        {keysProvided 
                            ? displayLoaded 
                                ? `총 ${displayClusters.length}개의 클러스터를 발견했습니다.`
                                : 'Kafka 클러스터 검색 준비 완료. 조회 버튼을 클릭하세요.'
                            : '액세스 키와 시크릿 키를 입력한 후 클러스터를 조회하세요.'
                        }
                    </QueryText>
                    <QueryButton 
                        onClick={fetchClusters} 
                        disabled={localLoading || !keysProvided}
                        $isLoading={localLoading}
                    >
                        <LoadingText $visible={localLoading}>
                            {displayLoaded ? '새로고침' : '클러스터 조회'}
                        </LoadingText>
                    </QueryButton>
                </QuerySection>
            )}
            
            {displayLoaded && displayClusters.length > 0 && (
                <ClusterList>
                    {displayClusters.map((cluster) => (
                        <ClusterOption
                            key={cluster.id}
                            $selected={selectedClusterId === cluster.id}
                        >
                            <RadioInput
                                type="radio"
                                name="kafka-cluster"
                                value={cluster.id}
                                checked={selectedClusterId === cluster.id}
                                onChange={() => handleClusterChange(cluster.id, cluster.bootstrap_servers)}
                            />
                            <ClusterInfo>
                                <ClusterName>
                                    {cluster.name}
                                    <StatusBadge $status={cluster.status}>
                                        {cluster.status}
                                    </StatusBadge>
                                </ClusterName>
                                <ClusterDetails>
                                    Kafka {cluster.version} · {cluster.total_broker_count}개 브로커 · {cluster.instance_type}
                                    <br />
                                    📡 {cluster.bootstrap_servers}
                                </ClusterDetails>
                            </ClusterInfo>
                        </ClusterOption>
                    ))}
                </ClusterList>
            )}

            {displayLoaded && displayClusters.length === 0 && (
                <EmptyState>사용 가능한 Kafka 클러스터가 없습니다.</EmptyState>
            )}
            
            {!displayLoaded && hideButton && (
                <EmptyState>통합 조회 버튼을 클릭하여 클러스터를 조회하세요.</EmptyState>
            )}
        </ToggleContainer>
    );
};

export default ClusterToggle;
