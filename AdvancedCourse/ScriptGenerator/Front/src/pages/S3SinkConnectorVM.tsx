import React, { useState } from 'react';
import InputBox from '../components/InputBox';
import ClusterToggle from '../components/ClusterToggle';
import ScriptDisplay from '../components/ScriptDisplay';
import styled from 'styled-components';
import axios from 'axios';
import usePersistedState from '../hooks/usePersistedState';
import { STORAGE_KEYS } from '../constants/storageKeys';

interface Cluster {
    id: string;
    name: string;
    status: string;
    version: string;
    bootstrap_servers: string;
    total_broker_count: number;
    instance_type: string;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

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

const S3SinkConnectorVM: React.FC = () => {
    const [accessKey, setAccessKey] = usePersistedState(STORAGE_KEYS.KAKAO_ACCESS_KEY, '');
    const [secretKey, setSecretKey] = usePersistedState(STORAGE_KEYS.KAKAO_SECRET_KEY, '');
    const [kafkaServer, setKafkaServer] = useState('');
    const [dataStreamVmIp, setDataStreamVmIp] = useState('');
    const [s3AccessKey, setS3AccessKey] = usePersistedState(STORAGE_KEYS.S3_ACCESS_KEY, '');
    const [s3SecretKey, setS3SecretKey] = usePersistedState(STORAGE_KEYS.S3_SECRET_KEY, '');
    const [script, setScript] = useState('');
    
    const [selectedClusterId, setSelectedClusterId] = useState('');
    const [kafkaClusters, setKafkaClusters] = useState<Cluster[]>([]);
    const [kafkaLoaded, setKafkaLoaded] = useState(false);
    const [integratedLoading, setIntegratedLoading] = useState(false);

    const handleKafkaQuery = async () => {
        if (!accessKey || !secretKey) {
            alert('액세스 키와 시크릿 키를 먼저 입력해야 함');
            return;
        }

        setIntegratedLoading(true);
        
        try {
            const kafkaResponse = await axios.post(`${API_BASE_URL}/get-kafka-clusters`, {
                access_key_id: accessKey,
                access_key_secret: secretKey,
            });
            
            const clusterDetails = kafkaResponse.data.cluster_details || [];
            setKafkaClusters(clusterDetails);
            setKafkaLoaded(true);
            
        } catch (error: any) {
            if (error.response?.status === 424) {
                alert('Kafka 클러스터 조회 실패\n\nKafka 서비스 권한이 없거나 클러스터가 존재하지 않을 수 있습니다.\n수동으로 입력해주세요.');
            } else {
                alert('Kafka 클러스터 조회 중 오류 발생');
            }
            setKafkaClusters([]);
            setKafkaLoaded(true);
        }
        
        setIntegratedLoading(false);
    };

    const handleClusterSelect = (clusterId: string, bootstrapServers: string) => {
        setSelectedClusterId(clusterId);
        setKafkaServer(bootstrapServers);
    };

    const generateScript = async () => {
        const newScript = `#!/bin/bash
# s3_sink_connector_init.sh
echo "kakaocloud: 1. 환경 변수 설정 시작"

cat <<'EOF' > /tmp/env_vars.sh
# 기존 리소스 정보
export KAFKA_BOOTSTRAP_SERVER="${kafkaServer}"
export SCHEMA_REGISTRY_SERVER="${dataStreamVmIp}"

# S3 인증 정보
export AWS_ACCESS_KEY_ID_VALUE="${s3AccessKey}"
export AWS_SECRET_ACCESS_KEY_VALUE="${s3SecretKey}"

# AWS 환경 변수 설정
export BUCKET_NAME="data-catalog-bucket"
export AWS_DEFAULT_REGION_VALUE="kr-central-2"
export AWS_DEFAULT_OUTPUT_VALUE="json"

# 로그 파일 경로
export LOGFILE="/home/ubuntu/setup.log"
EOF

# 환경 변수 적용 
source /tmp/env_vars.sh
echo "source /tmp/env_vars.sh" >> /home/ubuntu/.bashrc

echo "kakaocloud: 2. 스크립트 다운로드 사이트 유효성 검사 시작"
SCRIPT_URL="https://raw.githubusercontent.com/kakaocloud-edu/tutorial/refs/heads/main/DataAnalyzeCourse/src/day1/Lab01/kafka/s3_sink_connector.sh"

curl -L --output /dev/null --silent --head --fail "$SCRIPT_URL" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
wget -q "$SCRIPT_URL"
chmod +x s3_sink_connector.sh
sudo -E ./s3_sink_connector.sh`;

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
            <Title>S3 Sink Connector VM 스크립트 생성</Title>
            <Subtitle>kakaocloud 교육용</Subtitle>
            
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
                <InputBox
                    label="4. 사용자 S3 액세스 키"
                    placeholder="직접 입력"
                    value={s3AccessKey}
                    onChange={(e) => setS3AccessKey(e.target.value)}
                />
                <InputBox
                    label="5. 사용자 S3 시크릿 키"
                    placeholder="직접 입력"
                    value={s3SecretKey}
                    onChange={(e) => setS3SecretKey(e.target.value)}
                />
            </GroupContainer>

            <IntegratedQueryContainer>
                <IntegratedQueryButton
                    onClick={handleKafkaQuery}
                    disabled={integratedLoading || !accessKey || !secretKey}
                    $isLoading={integratedLoading}
                >
                    <LoadingText $visible={integratedLoading}>
                        Kafka 클러스터 조회
                    </LoadingText>
                </IntegratedQueryButton>
            </IntegratedQueryContainer>

            <GroupContainer>
                <ClusterToggle
                    label="6. Kafka 클러스터 선택"
                    selectedClusterId={selectedClusterId}
                    onClusterSelect={handleClusterSelect}
                    clusters={kafkaClusters}
                    isLoaded={kafkaLoaded}
                    hideButton={true}
                />
                <InputBox
                    label="7. Kafka 부트스트랩 서버"
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

export default S3SinkConnectorVM;
