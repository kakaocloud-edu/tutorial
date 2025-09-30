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

  ${props =>
    props.$isLoading
      ? `
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
  `
      : ''}

  @keyframes spin {
    0% {
      transform: translate(-50%, -50%) rotate(0deg);
    }
    100% {
      transform: translate(-50%, -50%) rotate(360deg);
    }
  }
`;

const LoadingText = styled.span<{ $visible: boolean }>`
  opacity: ${props => (props.$visible ? 0 : 1)};
  transition: opacity 0.2s ease;
`;

const ButtonContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2em;
  gap: 1em;
  flex-wrap: wrap;
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
  margin: 0 0.5em;

  &:hover {
    background-color: #ffec4f;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 8px rgba(255, 205, 0, 0.6);
  }
`;

const HadoopSetting: React.FC = () => {
  const [accessKey, setAccessKey] = usePersistedState(STORAGE_KEYS.KAKAO_ACCESS_KEY, '');
  const [secretKey, setSecretKey] = usePersistedState(STORAGE_KEYS.KAKAO_SECRET_KEY, '');
  const [s3AccessKey, setS3AccessKey] = usePersistedState(STORAGE_KEYS.S3_ACCESS_KEY, '');
  const [s3SecretKey, setS3SecretKey] = usePersistedState(STORAGE_KEYS.S3_SECRET_KEY, '');

  const [script, setScript] = useState('');
  const [dataStreamVmIp, setDataStreamVmIp] = useState('');
  const [selectedClusterId, setSelectedClusterId] = useState('');
  const [kafkaClusters, setKafkaClusters] = useState<Cluster[]>([]);
  const [kafkaLoaded, setKafkaLoaded] = useState(false);
  const [kafkaServer, setKafkaServer] = useState('');
  const [selectedInstanceName, setSelectedInstanceName] = useState('');
  const [mysqlInstances, setMysqlInstances] = useState<string[]>([]);
  const [mysqlLoaded, setMysqlLoaded] = useState(false);
  const [mysqlEndpoint, setMysqlEndpoint] = useState('');
  const [integratedLoading, setIntegratedLoading] = useState(false);

  const handleIntegratedQuery = async () => {
    if (!accessKey || !secretKey) {
      alert('액세스 키와 시크릿 키를 먼저 입력해야 함');
      return;
    }

    setIntegratedLoading(true);

    try {
      const [kafkaResponse, mysqlResponse] = await Promise.all([
        axios.post(`${API_BASE_URL}/get-kafka-clusters`, {
          access_key_id: accessKey,
          access_key_secret: secretKey,
        }),
        axios.post(`${API_BASE_URL}/get-instance-groups`, {
          access_key_id: accessKey,
          access_key_secret: secretKey,
        }),
      ]);

      const clusterDetails = kafkaResponse.data.cluster_details || [];
      setKafkaClusters(clusterDetails);
      setKafkaLoaded(true);

      const instanceNames = mysqlResponse.data || [];
      setMysqlInstances(instanceNames);
      setMysqlLoaded(true);
    } catch (error: any) {
      if (error.response?.status === 424) {
        alert(
          '리소스 조회 실패\n\n일부 서비스 권한이 없거나 리소스가 존재하지 않을 수 있습니다.\n수동으로 입력해주세요.'
        );
      } else {
        alert('리소스 조회 중 오류 발생');
      }
      setKafkaClusters([]);
      setMysqlInstances([]);
      setKafkaLoaded(true);
      setMysqlLoaded(true);
    }

    setIntegratedLoading(false);
  };

  const handleClusterSelect = (clusterId: string, bootstrapServers: string) => {
    setSelectedClusterId(clusterId);
    setKafkaServer(bootstrapServers);
  };

  const handleInstanceSelect = async (instanceName: string) => {
    setSelectedInstanceName(instanceName);

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

  const generateHadoopConfig = async () => {
    const hadoopConfig = {
      configurations: [
        {
          classification: 'core-site',
          properties: {
            'fs.swifta.service.kic.credential.id': accessKey,
            'fs.swifta.service.kic.credential.secret': secretKey,
            'fs.s3a.access.key': s3AccessKey,
            'fs.s3a.secret.key': s3SecretKey,
            'fs.s3a.buckets.create.region': 'kr-central-2',
            'fs.s3a.endpoint.region': 'kr-central-2',
            'fs.s3a.endpoint': 'objectstorage.kr-central-2.kakaocloud.com',
            's3service.s3-endpoint': 'objectstorage.kr-central-2.kakaocloud.com',
          },
        },
      ],
    };

    const formattedJson = JSON.stringify(hadoopConfig, null, 2);
    setScript(formattedJson);
    await copyToClipboard(formattedJson, '클러스터 구성 설정');
  };

  const saveTextAsFile = (filename: string, text: string) => {
    const sanitizedText = text.replace(/\r/g, ''); // CR 제거
    const blob = new Blob([sanitizedText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  const generateAllScripts = async () => {
    if (!mysqlEndpoint || !kafkaServer || !dataStreamVmIp) {
      alert('모든 필수 정보를 입력해주세요.');
      return;
    }

    const allScripts = `#!/bin/bash
set -x
exec > >(logger -t HADOOP-ENV) 2>&1

echo "Hadoop environment variables setup start"

# Wait for ubuntu user directory
timeout=30
count=0
while [ ! -d "/home/ubuntu" ] && [ $count -lt $timeout ]; do
    echo "Waiting for ubuntu user... ($count/$timeout)"
    sleep 2
    count=$((count + 1))
done

if [ ! -d "/home/ubuntu" ]; then
    echo "Ubuntu user directory not found"
    exit 1
fi

# Check if variables already exist to prevent duplicates
if ! grep -q "MYSQL_HOST=" /home/ubuntu/.bashrc; then
    echo "" >> /home/ubuntu/.bashrc
    echo "# Hadoop Cluster Environment Variables" >> /home/ubuntu/.bashrc
    echo "export MYSQL_HOST=${mysqlEndpoint}" >> /home/ubuntu/.bashrc
    echo "export SCHEMA_REGISTRY_SERVER=${dataStreamVmIp}" >> /home/ubuntu/.bashrc
    echo "export KAFKA_BOOTSTRAP_SERVERS=${kafkaServer}" >> /home/ubuntu/.bashrc

    chown ubuntu:ubuntu /home/ubuntu/.bashrc
    echo "Environment variables added to .bashrc"
else
    echo "Environment variables already exist in .bashrc"
fi
source /home/ubuntu/.bashrc

echo "Hadoop environment setup completed"
`;

    setScript(allScripts);
    saveTextAsFile('hadoop_user_script.sh', allScripts);
  };

  const copyToClipboard = async (text: string, scriptType: string) => {
    try {
      const sanitizedText = text.replace(/\r/g, ''); // CR 제거
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(sanitizedText);
        alert(`${scriptType} 생성 및 클립보드에 복사`);
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = sanitizedText;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert(`${scriptType} 생성 및 클립보드에 복사`);
      }
    } catch (err) {
      alert('클립보드 복사 중 오류 발생');
    }
  };

  return (
    <Container>
      <Title>Hadoop Configuration 설정</Title>
      <Subtitle>kakaocloud 교육용</Subtitle>

      {/* 1단계: 액세스 키, 시크릿 키, DataStream VM IP */}
      <GroupContainer>
        <InputBox label="1. 사용자 액세스 키" placeholder="직접 입력" value={accessKey} onChange={e => setAccessKey(e.target.value)} />
        <InputBox label="2. 사용자 시크릿 키" placeholder="직접 입력" value={secretKey} onChange={e => setSecretKey(e.target.value)} />
        <InputBox label="3. DataStream VM의 Private IP" placeholder="ex) 1.2.3.4 (직접 입력 필요)" value={dataStreamVmIp} onChange={e => setDataStreamVmIp(e.target.value)} />
        <InputBox label="4. 사용자 S3 액세스 키" placeholder="직접 입력" value={s3AccessKey} onChange={e => setS3AccessKey(e.target.value)} />
        <InputBox label="5. 사용자 S3 시크릿 키" placeholder="직접 입력" value={s3SecretKey} onChange={e => setS3SecretKey(e.target.value)} />
      </GroupContainer>

      {/* 2단계: 통합 리소스 조회 */}
      <IntegratedQueryContainer>
        <IntegratedQueryButton onClick={handleIntegratedQuery} disabled={integratedLoading || !accessKey || !secretKey} $isLoading={integratedLoading}>
          <LoadingText $visible={integratedLoading}>전체 리소스 조회</LoadingText>
        </IntegratedQueryButton>
      </IntegratedQueryContainer>

      {/* 3단계: Kafka 클러스터 선택 */}
      <GroupContainer>
        <ClusterToggle
          label="6. Kafka 클러스터 선택"
          selectedClusterId={selectedClusterId}
          onClusterSelect={handleClusterSelect}
          clusters={kafkaClusters}
          isLoaded={kafkaLoaded}
          hideButton={true}
        />
        <InputBox label="7. Kafka 부트스트랩 서버" placeholder="위에서 클러스터 선택 시 자동 입력" value={kafkaServer} onChange={e => setKafkaServer(e.target.value)} />
      </GroupContainer>

      {/* 4단계: MySQL 인스턴스 선택 */}
      <GroupContainer>
        <MySQLInstanceToggle
          label="8. MySQL 인스턴스 선택"
          selectedInstanceName={selectedInstanceName}
          onInstanceSelect={handleInstanceSelect}
          instances={mysqlInstances}
          isLoaded={mysqlLoaded}
          hideButton={true}
        />
        <InputBox label="9. MySQL 엔드포인트" placeholder="위에서 인스턴스 선택 시 자동 입력" value={mysqlEndpoint} onChange={e => setMysqlEndpoint(e.target.value)} />
      </GroupContainer>

      <ScriptDisplay script={script} />

      <ButtonContainer>
        <StyledButton onClick={generateAllScripts}>사용자 스크립트 다운로드</StyledButton>
        <StyledButton onClick={generateHadoopConfig}>클러스터 구성 설정</StyledButton>
      </ButtonContainer>
    </Container>
  );
};

export default HadoopSetting;
