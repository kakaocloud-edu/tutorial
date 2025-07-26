import React, { useState } from 'react';
import styled, { keyframes, css } from 'styled-components';
import axios from 'axios';

// 기존 스타일 컴포넌트들은 ClusterToggle과 동일한 패턴으로 유지...

const spin = keyframes`
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
`;

// ... (기존 스타일 컴포넌트들)

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

const InstanceList = styled.div`
    display: flex;
    flex-direction: column;
    gap: 0.5em;
    max-height: 200px;
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

const InstanceOption = styled.label<{ $selected: boolean }>`
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

const InstanceInfo = styled.div`
    flex: 1;
    color: #fff;
`;

const InstanceName = styled.div`
    font-weight: bold;
    margin-bottom: 0.4em;
    font-size: 1em;
`;

const InstanceDetails = styled.div`
    font-size: 0.85em;
    color: #ccc;
    line-height: 1.4;
`;

const EmptyState = styled.div`
    text-align: center;
    color: #999;
    padding: 2em 1em;
    font-style: italic;
`;

// 수정된 인터페이스
interface MySQLInstanceToggleProps {
    label: string;
    selectedInstanceName: string;
    onInstanceSelect: (instanceName: string) => void;
    
    // 기존 방식 (개별 조회) - 선택적
    accessKey?: string;
    secretKey?: string;
    
    // 새로운 방식 (통합 조회) - 선택적
    instances?: string[];
    isLoaded?: boolean;
    hideButton?: boolean;
}

const MySQLInstanceToggle: React.FC<MySQLInstanceToggleProps> = ({
    label,
    selectedInstanceName,
    onInstanceSelect,
    accessKey = '',
    secretKey = '',
    instances = [],
    isLoaded = false,
    hideButton = false
}) => {
    const [localInstances, setLocalInstances] = useState<string[]>([]);
    const [localLoading, setLocalLoading] = useState(false);
    const [localLoaded, setLocalLoaded] = useState(false);

    // 기존 개별 조회 로직
    const fetchInstances = async () => {
        if (!accessKey || !secretKey) {
            alert('액세스 키와 시크릿 키를 먼저 입력해주세요.');
            return;
        }

        setLocalLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/get-instance-groups', {
                access_key_id: accessKey,
                access_key_secret: secretKey,
            });
            
            const instanceNames = response.data || [];
            setLocalInstances(instanceNames);
            setLocalLoaded(true);
            
            if (instanceNames.length === 0) {
                alert('사용 가능한 MySQL 인스턴스가 없습니다.');
            }
        } catch (error) {
            console.error('MySQL 인스턴스 조회 오류:', error);
            alert('MySQL 인스턴스 조회 중 오류가 발생했습니다.');
            setLocalInstances([]);
        }
        setLocalLoading(false);
    };

    const handleInstanceChange = (instanceName: string) => {
        onInstanceSelect(instanceName);
    };

    // 외부에서 전달받은 데이터가 있으면 그것을 우선 사용, 없으면 로컬 데이터 사용
    const displayInstances = instances.length > 0 ? instances : localInstances;
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
                                ? `총 ${displayInstances.length}개의 MySQL 인스턴스를 발견했습니다.`
                                : 'MySQL 인스턴스 검색 준비 완료. 조회 버튼을 클릭하세요.'
                            : '액세스 키와 시크릿 키를 입력한 후 인스턴스를 조회하세요.'
                        }
                    </QueryText>
                    <QueryButton 
                        onClick={fetchInstances} 
                        disabled={localLoading || !keysProvided}
                        $isLoading={localLoading}
                    >
                        <LoadingText $visible={localLoading}>
                            {displayLoaded ? '새로고침' : '인스턴스 조회'}
                        </LoadingText>
                    </QueryButton>
                </QuerySection>
            )}
            
            {displayLoaded && displayInstances.length > 0 && (
                <InstanceList>
                    {displayInstances.map((instanceName) => (
                        <InstanceOption
                            key={instanceName}
                            $selected={selectedInstanceName === instanceName}
                        >
                            <RadioInput
                                type="radio"
                                name="mysql-instance"
                                value={instanceName}
                                checked={selectedInstanceName === instanceName}
                                onChange={() => handleInstanceChange(instanceName)}
                            />
                            <InstanceInfo>
                                <InstanceName>
                                    🗄️ {instanceName}
                                </InstanceName>
                                <InstanceDetails>
                                    MySQL 인스턴스 세트
                                </InstanceDetails>
                            </InstanceInfo>
                        </InstanceOption>
                    ))}
                </InstanceList>
            )}

            {displayLoaded && displayInstances.length === 0 && (
                <EmptyState>사용 가능한 MySQL 인스턴스가 없습니다.</EmptyState>
            )}
            
            {!displayLoaded && hideButton && (
                <EmptyState>통합 조회 버튼을 클릭하여 인스턴스를 조회하세요.</EmptyState>
            )}
        </ToggleContainer>
    );
};

export default MySQLInstanceToggle;
