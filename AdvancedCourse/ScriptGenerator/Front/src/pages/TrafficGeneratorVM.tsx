import React, { useState } from 'react';
import InputBox from '../components/InputBox';
import ClusterToggle from '../components/ClusterToggle';
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

const TrafficGeneratorVM: React.FC = () => {
    const [accessKey, setAccessKey] = usePersistedState(STORAGE_KEYS.KAKAO_ACCESS_KEY, '');
    const [secretKey, setSecretKey] = usePersistedState(STORAGE_KEYS.KAKAO_SECRET_KEY, '');
    const [projectName, setProjectName] = useState('');
    const [domainId, setDomainId] = useState('');
    const [projectId, setProjectId] = useState('');
    const [albIp, setAlbIp] = useState('');
    const [kafkaServer, setKafkaServer] = useState('');
    const [script, setScript] = useState('');
    
    // Kafka 클러스터 관련 상태
    const [selectedClusterId, setSelectedClusterId] = useState('');
    const [kafkaClusters, setKafkaClusters] = useState<Cluster[]>([]);
    const [kafkaLoaded, setKafkaLoaded] = useState(false);
    
    // 통합 조회 로딩 상태
    const [integratedLoading, setIntegratedLoading] = useState(false);

    // 통합 API 조회 (프로젝트 정보 + Kafka 클러스터 동시 조회)
    const handleIntegratedQuery = async () => {
        if (!accessKey || !secretKey) {
            alert('액세스 키와 시크릿 키를 먼저 입력해야 함');
            return;
        }

        setIntegratedLoading(true);
        
        try {
            // 토큰 세부 정보와 Kafka 클러스터 동시 조회
            const [tokenResponse, kafkaResponse] = await Promise.all([
                axios.post(`${API_BASE_URL}/get-token-details`, {
                    access_key_id: accessKey,
                    access_key_secret: secretKey,
                }),
                axios.post(`${API_BASE_URL}/get-kafka-clusters`, {
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
            
            // 조용한 완료 처리
            console.log('통합 조회 완료:', {
                project: tokenResponse.data.project_name,
                domain: tokenResponse.data.domain_id,
                projectId: tokenResponse.data.project_id,
                kafkaClusters: clusterDetails.length
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

    const generateScript = async () => {
        const newScript = `#!/bin/bash
# tg_vm_init.sh
set -e  # 오류 발생 시 스크립트 종료

echo "kakaocloud: 1.환경 변수 설정 시작"
# 환경 변수 정의
command=$(cat <<EOF
# 프로젝트 및 인증 정보
export DOMAIN_ID="${domainId}"
export PROJECT_ID="${projectId}"
export CREDENTIAL_ID="${accessKey}"
export CREDENTIAL_SECRET="${secretKey}"

# 생성한 리소스의 값
export API_BASE_URL="${albIp}"
export KAFKA_BOOTSTRAP_SERVERS="${kafkaServer}"
export TOPIC_NAME="test-topic"
export SUB_NAME="test-pull-sub"

# 생성할 Pub/Sub 리소스 정보
export TOPIC_NAME_MK="log-topic"
export OBJECT_STORAGE_SUBSCRIPTION_NAME="log-obj-sub"
export OBJECT_STORAGE_BUCKET="pubsub-log-bucket"
export PUBSUB_ENDPOINT="https://pub-sub.kr-central-2.kakaocloud.com"

# Kafka 실행에 필요한 경로 및 정보
export KAFKA_HOME=/opt/kafka
export PATH=$PATH:$KAFKA_HOME/bin
EOF
)

# 환경 변수 적용
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc

echo "kakaocloud: 2.스크립트 다운로드 사이트 유효성 검사 시작"
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/tg_full_setup.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }

wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day1/Lab01/traffic_generator/tg_full_setup.sh
chmod +x tg_full_setup.sh
sudo -E ./tg_full_setup.sh`;

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
            <Title>트래픽 생성기 VM 스크립트 생성</Title>
            <Subtitle>kakaocloud 교육용</Subtitle>
            
            {/* 1단계: 액세스 키, 시크릿 키, ALB IP (직접 입력) */}
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
                    label="3. ALB의 Public IP"
                    placeholder="ex) 1.2.3.4 (직접 입력 필요)"
                    value={albIp}
                    onChange={(e) => setAlbIp(e.target.value)}
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

            <ScriptDisplay script={script} />
            <ButtonContainer>
                <StyledButton onClick={generateScript}>스크립트 생성 및 복사</StyledButton>
            </ButtonContainer>
        </Container>
    );
};

export default TrafficGeneratorVM;
