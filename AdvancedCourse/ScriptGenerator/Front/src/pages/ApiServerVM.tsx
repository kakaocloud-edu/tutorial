import React, { useState } from 'react';
import InputBox from '../components/InputBox';
import ClusterToggle from '../components/ClusterToggle';
import MySQLInstanceToggle from '../components/MySQLInstanceToggle';
import ScriptDisplay from '../components/ScriptDisplay';
import styled from 'styled-components';
import axios from 'axios';
import usePersistedState from '../hooks/usePersistedState';
import { STORAGE_KEYS } from '../constants/storageKeys';

// API URL 환경변수
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Cluster 인터페이스 정의
interface Cluster {
    id: string;
    name: string;
    status: string;
    version: string;
    bootstrap_servers: string;
    total_broker_count: number;
    instance_type: string;
}

const Container = styled.div`
    max-width: 800px;
    margin: 2em auto;
    padding: 2em;
    background-color: rgba(0, 0, 0, 0.5);
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    z-index: 10;
    min-height: 100vh;
`;

const Title = styled.h1`
    text-align: center;
    margin-top: 0.65em;
    margin-bottom: 0.5em;
    color: #fff;
`;

const Subtitle = styled.h3`
    text-align: center;
    margin-bottom: 1.5em;
    color: #ffe100;
    font-size: 1.2em;
    font-weight: normal;
`;

const GroupContainer = styled.div`
    margin-bottom: 1.5em;
    padding: 1em;
    padding-top: 2em;
    padding-bottom: 0.01em;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
`;

// 통합 조회 버튼 컨테이너
const IntegratedQueryContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 1.5em 0;
    padding: 1.5em;
    background: linear-gradient(135deg, rgba(255, 225, 0, 0.15) 0%, rgba(255, 225, 0, 0.08) 100%);
    border: 2px solid rgba(255, 225, 0, 0.4);
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(255, 225, 0, 0.2);
`;

const IntegratedQueryButton = styled.button<{ $isLoading: boolean }>`
    background: linear-gradient(135deg, #ffe100 0%, #ffec4f 100%);
    color: #000;
    border: none;
    padding: 1.2em 2.5em;
    border-radius: 30px;
    cursor: pointer;
    font-size: 1.1em;
    font-weight: bold;
    transition: all 0.3s ease;
    position: relative;
    min-width: 250px;
    box-shadow: 0 6px 20px rgba(255, 225, 0, 0.4);
    
    &:hover:not(:disabled) {
        background: linear-gradient(135deg, #ffec4f 0%, #fff176 100%);
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(255, 225, 0, 0.5);
    }
    
    &:disabled {
        background: #666;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    ${props => props.$isLoading ? `
        &::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            margin: auto;
            border: 3px solid #000;
            border-top: 3px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
    ` : ''}
    
    @keyframes spin {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
`;

const LoadingText = styled.span<{ $visible: boolean }>`
    opacity: ${props => props.$visible ? 0 : 1};
    transition: opacity 0.2s ease;
`;

const ButtonContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 2em;
`;

const StyledButton = styled.button`
    background-color: #ffe100;
    color: black;
    border: none;
    padding: 0.75em 1.5em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    transition: background-color 0.1s ease-in;
    margin: 0 1em;

    &:hover {
        background-color: #FFEC4F;
    }

    &:focus {
        outline: none;
        box-shadow: 0 0 8px rgba(255, 205, 0, 0.6);
    }
`;

const ApiServerVM: React.FC = () => {
    const [accessKey, setAccessKey] = usePersistedState(STORAGE_KEYS.KAKAO_ACCESS_KEY, '');
    const [secretKey, setSecretKey] = usePersistedState(STORAGE_KEYS.KAKAO_SECRET_KEY, '');
    const [projectName, setProjectName] = useState('');
    const [domainId, setDomainId] = useState('');
    const [projectId, setProjectId] = useState('');
    const [mysqlEndpoint, setMysqlEndpoint] = useState('');
    const [dataStreamVmIp, setDataStreamVmIp] = useState('');
    const [kafkaServer, setKafkaServer] = useState('');
    const [script, setScript] = useState('');
    
    // Kafka 클러스터 관련 상태
    const [selectedClusterId, setSelectedClusterId] = useState('');
    const [kafkaClusters, setKafkaClusters] = useState<Cluster[]>([]);
    const [kafkaLoaded, setKafkaLoaded] = useState(false);
    
    // MySQL 인스턴스 관련 상태
    const [selectedInstanceName, setSelectedInstanceName] = useState('');
    const [mysqlInstances, setMysqlInstances] = useState<string[]>([]);
    const [mysqlLoaded, setMysqlLoaded] = useState(false);
    
    // 통합 조회 로딩 상태
    const [integratedLoading, setIntegratedLoading] = useState(false);

    // 통합 API 조회 (프로젝트 정보 + Kafka + MySQL 동시 조회)
    const handleIntegratedQuery = async () => {
        if (!accessKey || !secretKey) {
            alert('액세스 키와 시크릿 키를 먼저 입력해야 함');
            return;
        }

        setIntegratedLoading(true);
        
        try {
            // 토큰 세부 정보, Kafka 클러스터, MySQL 인스턴스 동시 조회
            const [tokenResponse, kafkaResponse, mysqlResponse] = await Promise.all([
                axios.post(`${API_BASE_URL}/get-token-details`, {
                    access_key_id: accessKey,
                    access_key_secret: secretKey,
                }),
                axios.post(`${API_BASE_URL}/get-kafka-clusters`, {
                    access_key_id: accessKey,
                    access_key_secret: secretKey,
                }),
                axios.post(`${API_BASE_URL}/get-instance-groups`, {
                    access_key_id: accessKey,
                    access_key_secret: secretKey,
                })
            ]);
            
            // 프로젝트 정보 설정
            setProjectName(tokenResponse.data.project_name || '');
            setDomainId(tokenResponse.data.domain_id || '');
            setProjectId(tokenResponse.data.project_id || '');
            
            // Kafka 클러스터 데이터 처리
            const clusterDetails = kafkaResponse.data.cluster_details || [];
            setKafkaClusters(clusterDetails);
            setKafkaLoaded(true);
            
            // MySQL 인스턴스 데이터 처리
            const instanceNames = mysqlResponse.data || [];
            setMysqlInstances(instanceNames);
            setMysqlLoaded(true);
            
            // 조용한 완료 처리
            console.log('통합 조회 완료:', {
                project: tokenResponse.data.project_name,
                domain: tokenResponse.data.domain_id,
                projectId: tokenResponse.data.project_id,
                kafkaClusters: clusterDetails.length,
                mysqlInstances: instanceNames.length
            });
            
        } catch (error) {
            console.error('통합 조회 오류:', error);
            alert('리소스 조회 중 오류 발생');
        }
        
        setIntegratedLoading(false);
    };

    // Kafka 클러스터 선택 처리
    const handleClusterSelect = (clusterId: string, bootstrapServers: string) => {
        setSelectedClusterId(clusterId);
        setKafkaServer(bootstrapServers);
    };

    // MySQL 인스턴스 선택 처리
    const handleInstanceSelect = async (instanceName: string) => {
        setSelectedInstanceName(instanceName);
        
        // 선택된 인스턴스의 엔드포인트 조회
        try {
            const response = await axios.post(`${API_BASE_URL}/get-instance-endpoints`, {
                access_key_id: accessKey,
                access_key_secret: secretKey,
                instance_set_name: instanceName,
            });
            
            const primaryEndpoint = response.data.primary_endpoint || '';
            setMysqlEndpoint(primaryEndpoint);
        } catch (error) {
            console.error('MySQL 엔드포인트 조회 오류:', error);
            alert('MySQL 엔드포인트 조회 중 오류 발생');
        }
    };

    const generateScript = async () => {
        const newScript = `#!/bin/bash
# api_vm_init.sh
# 프로젝트 및 인증 정보
export DOMAIN_ID="${domainId}"
export PROJECT_ID="${projectId}"
export CREDENTIAL_ID="${accessKey}"
export CREDENTIAL_SECRET="${secretKey}"

# 데이터베이스 설정
export MYSQL_HOST="${mysqlEndpoint}"

# 스키마 레지스트리 설정
export SCHEMA_REGISTRY_URL="${dataStreamVmIp}"

# Pub/Sub 및 Kafka 설정
export LOGSTASH_KAFKA_ENDPOINT="${kafkaServer}"
export PUBSUB_TOPIC_NAME="log-topic"
export KAFKA_TOPIC_NAME="nginx-topic"

# 로그 및 환경 설정
export LOGSTASH_ENV_FILE="/etc/default/logstash"
export ENV_SETUP_SCRIPT_URL="https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/api_server/api_env_setup.sh"

echo "kakaocloud: 1. api server VM 환경 설정용 api_env_setup.sh 다운로드"
curl --output /dev/null --silent --head --fail "$ENV_SETUP_SCRIPT_URL" || {
  echo "kakaocloud: api_env_setup.sh 다운로드 링크가 유효하지 않습니다."
  exit 1
}

wget -O api_env_setup.sh "$ENV_SETUP_SCRIPT_URL"

echo "kakaocloud: 2. api_env_setup.sh 실행"
chmod +x api_env_setup.sh
sudo -E ./api_env_setup.sh`;

        setScript(newScript);

        try {
            await navigator.clipboard.writeText(newScript);
            alert('스크립트가 생성되고 클립보드에 복사됨');
        } catch (err) {
            alert('클립보드 복사 중 오류 발생');
        }
    };

    return (
        <Container>
            <Title>API Server VM 스크립트 생성</Title>
            <Subtitle>kakaocloud 교육용</Subtitle>
            
            {/* 1단계: 액세스 키, 시크릿 키, DataStream VM IP (직접 입력) */}
            <GroupContainer>
                <InputBox
                    label="1. 사용자 액세스 키"
                    placeholder="직접 입력"
                    value={accessKey}
                    onChange={(e) => setAccessKey(e.target.value)}
                />
                <InputBox
                    label="2. 사용자 시크릿 키"
                    placeholder="직접 입력"
                    value={secretKey}
                    onChange={(e) => setSecretKey(e.target.value)}
                />
                <InputBox
                    label="3. DataStream VM의 Public IP"
                    placeholder="ex) 1.2.3.4 (직접 입력 필요)"
                    value={dataStreamVmIp}
                    onChange={(e) => setDataStreamVmIp(e.target.value)}
                />
            </GroupContainer>

            {/* 2단계: 통합 API 조회 버튼 */}
            <IntegratedQueryContainer>
                <IntegratedQueryButton
                    onClick={handleIntegratedQuery}
                    disabled={integratedLoading || !accessKey || !secretKey}
                    $isLoading={integratedLoading}
                >
                    <LoadingText $visible={integratedLoading}>
                        전체 리소스 조회
                    </LoadingText>
                </IntegratedQueryButton>
            </IntegratedQueryContainer>

            {/* 3단계: 프로젝트 정보 (통합 조회로 자동 입력) */}
            <GroupContainer>
                <InputBox
                    label="4. 프로젝트 이름"
                    placeholder="위의 통합 조회 버튼 클릭 시 자동 입력"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                />
                <InputBox
                    label="5. 조직 ID"
                    placeholder="위의 통합 조회 버튼 클릭 시 자동 입력"
                    value={domainId}
                    onChange={(e) => setDomainId(e.target.value)}
                />
                <InputBox
                    label="6. 프로젝트 ID"
                    placeholder="위의 통합 조회 버튼 클릭 시 자동 입력"
                    value={projectId}
                    onChange={(e) => setProjectId(e.target.value)}
                />
            </GroupContainer>

            {/* 4단계: Kafka 클러스터 선택 */}
            <GroupContainer>
                <ClusterToggle
                    label="7. Kafka 클러스터 선택"
                    selectedClusterId={selectedClusterId}
                    onClusterSelect={handleClusterSelect}
                    clusters={kafkaClusters}
                    isLoaded={kafkaLoaded}
                    hideButton={true}
                />
                <InputBox
                    label="8. Kafka 부트스트랩 서버"
                    placeholder="위에서 클러스터 선택 시 자동 입력"
                    value={kafkaServer}
                    onChange={(e) => setKafkaServer(e.target.value)}
                />
            </GroupContainer>

            {/* 5단계: MySQL 인스턴스 선택 */}
            <GroupContainer>
                <MySQLInstanceToggle
                    label="9. MySQL 인스턴스 선택"
                    selectedInstanceName={selectedInstanceName}
                    onInstanceSelect={handleInstanceSelect}
                    instances={mysqlInstances}
                    isLoaded={mysqlLoaded}
                    hideButton={true}
                />
                <InputBox
                    label="10. MySQL 엔드포인트"
                    placeholder="위에서 인스턴스 선택 시 자동 입력"
                    value={mysqlEndpoint}
                    onChange={(e) => setMysqlEndpoint(e.target.value)}
                />
            </GroupContainer>

            <ScriptDisplay script={script} />
            <ButtonContainer>
                <StyledButton onClick={generateScript}>스크립트 생성 및 복사</StyledButton>
            </ButtonContainer>
        </Container>
    );
};

export default ApiServerVM;
