import React, { useEffect, useState } from 'react';
import InputBox from '../components/InputBox';
import ScriptDisplay from '../components/ScriptDisplay';
import SelectBox from '../components/SelectBox';
import styled from 'styled-components';
import axios from 'axios';
import usePersistedState from '../hooks/usePersistedState';
import { STORAGE_KEYS } from '../constants/storageKeys';

// API URL 환경변수
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

interface KubeConfig {
    clusters: Array<{
        cluster: {
            "certificate-authority-data": string;
            server: string;
        };
        name: string;
    }>;
}

const MainPage: React.FC = () => {
    const [accessKey, setAccessKey] = usePersistedState(STORAGE_KEYS.KAKAO_ACCESS_KEY, '');
    const [secretKey, setSecretKey] = usePersistedState(STORAGE_KEYS.KAKAO_SECRET_KEY, '');
    const [projectName, setProjectName] = useState('');
    const [clusterList, setClusterList] = useState<string[]>([]);
    const [clusterName, setClusterName] = useState('');
    const [apiEndpoint, setApiEndpoint] = useState('');
    const [authData, setAuthData] = useState('');
    const [instanceList, setInstanceList] = useState('');
    const [instanceName, setInstanceName] = useState('');
    const [primaryEndpoint, setPrimaryEndpoint] = useState('');
    const [standbyEndpoint, setStandbyEndpoint] = useState('');
    const [dockerImageName, setDockerImageName] = useState('demo-spring-boot');
    const [dockerJavaVersion, setDockerJavaVersion] = useState('17-jdk-slim');
    const [script, setScript] = useState('');
    const [loading, setLoading] = useState(false);
    const [loadingButton, setLoadingButton] = useState<string | null>(null);
    const [instanceEndpoints, setInstanceEndpoints] = useState<{ [key: string]: { primary_endpoint: string, standby_endpoint: string } }>({});
    const [errors, setErrors] = useState<{ [key: string]: string }>({});

    const handleApiButtonClick = async (id: string, apiFunction: (arg?: string) => Promise<void>, arg?: string) => {
        setLoadingButton(id);
        try {
            await apiFunction(arg);
        } finally {
            setLoadingButton(null);
        }
    };

    const handleInstanceNameChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedInstanceName = event.target.value;
        setInstanceName(selectedInstanceName);
        handleApiButtonClick('fetchInstanceEndpoints', fetchInstanceEndpoints, selectedInstanceName);
    };

    const handleClusterNameChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedClusterName = event.target.value;
        setClusterName(selectedClusterName);
        handleApiButtonClick('fetchKubeConfig', fetchKubeConfig, selectedClusterName);
    };

    const handleFetchProjectsAndClusters = async () => {
        await fetchProjects();
        await fetchClusters();
        await fetchInstanceLists();
    };

    const validateForm = () => {
        const newErrors: { [key: string]: string } = {};
        let isValid = true;

        // 액세스 키 유효성 검사
        if (accessKey.length < 32) {
            isValid = false;
            newErrors.accessKey = '액세스 키는 최소 32자리여야 합니다.';
        } else if (!/^[a-z0-9]+$/.test(accessKey)) {
            isValid = false;
            newErrors.accessKey = '액세스 키는 소문자와 숫자로만 구성되어야 합니다.';
        }

        // 비밀 액세스 키 유효성 검사
        if (secretKey.length < 64) {
            isValid = false;
            newErrors.secretKey = '비밀 액세스 키는 최소 64자리여야 합니다.';
        } else if (!/^[a-z0-9]+$/.test(secretKey)) {
            isValid = false;
            newErrors.secretKey = '비밀 액세스 키는 소문자와 숫자로만 구성되어야 합니다.';
        }

        // 클러스터 이름 유효성 검사
        if (!/^[a-z]/.test(clusterName)) {
            isValid = false;
            newErrors.clusterName = '클러스터 이름은 영어 소문자로 시작해야 합니다.';
        } else if (!/^[a-z0-9-]+$/.test(clusterName)) {
            isValid = false;
            newErrors.clusterName = '클러스터 이름은 소문자, 숫자, "-"만 사용해야 합니다.';
        } else if (clusterName.length < 4 || clusterName.length > 20) {
            isValid = false;
            newErrors.clusterName = '클러스터 이름은 4~20자리여야 합니다.';
        }

        // API 엔드포인트 유효성 검사
        const apiEndpointPattern = /^https:\/\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-public\.ke\.kr-central-2\.kakaocloud\.com$/;
        if (!apiEndpointPattern.test(apiEndpoint)) {
            isValid = false;
            newErrors.apiEndpoint = 'API 엔드포인트 형식이 유효하지 않습니다.';
        }

        // 인증 데이터 유효성 검사
        const authDataPattern = /^[A-Za-z0-9+/=]+$/;
        if (!authDataPattern.test(authData)) {
            isValid = false;
            newErrors.authData = '인증 데이터는 유효한 Base64 형식이어야 합니다.';
        } else if (!authData.endsWith('=')) {
            isValid = false;
            newErrors.authData = '인증 데이터는 "="로 끝나야 합니다.';
        } else {
            try {
                const decodedAuthData = atob(authData);
                const pemPattern = /-----BEGIN CERTIFICATE-----[\s\S]+-----END CERTIFICATE-----/;
                if (!pemPattern.test(decodedAuthData)) {
                    isValid = false;
                    newErrors.authData = '인증 데이터는 유효한 PEM 형식의 인증서여야 합니다.';
                }
            } catch (e) {
                isValid = false;
                newErrors.authData = '인증 데이터를 Base64로 디코딩할 수 없습니다.';
            }
        }

        // 프로젝트명 유효성 검사
        if (!/^[a-z]/.test(projectName)) {
            isValid = false;
            newErrors.projectName = '프로젝트명은 영어 소문자로 시작해야 합니다.';
        } else if (!/^[a-z0-9-]+$/.test(projectName)) {
            isValid = false;
            newErrors.projectName = '프로젝트명은 소문자, 숫자, "-"만 사용해야 합니다.';
        } else if (projectName.length < 4 || projectName.length > 30) {
            isValid = false;
            newErrors.projectName = '프로젝트명은 4~30자리여야 합니다.';
        }

        // Primary 엔드포인트 유효성 검사
        if (!primaryEndpoint.startsWith('az-')) {
            isValid = false;
            newErrors.primaryEndpoint = 'Primary 엔드포인트는 az-a 또는 az-b로 시작해야 합니다.';
        } else {
            const primaryParts = primaryEndpoint.split('.');
            if (primaryParts.length < 6 || (primaryParts[0] !== 'az-a' && primaryParts[0] !== 'az-b')) {
                isValid = false;
                newErrors.primaryEndpoint = 'Primary 엔드포인트 형식이 유효하지 않습니다.';
            } else if (!/^[0-9a-f]{32}$/.test(primaryParts[2])) {
                isValid = false;
                newErrors.primaryEndpoint = 'Primary 엔드포인트의 UUID 형식이 유효하지 않습니다.';
            } else if (primaryParts.slice(3).join('.') !== 'mysql.managed-service.kr-central-2.kakaocloud.com') {
                isValid = false;
                newErrors.primaryEndpoint = 'Primary 엔드포인트는 "mysql.managed-service.kr-central-2.kakaocloud.com"로 끝나야 합니다.';
            }
        }

        // Standby 엔드포인트 유효성 검사
        if (!standbyEndpoint.startsWith('az-')) {
            isValid = false;
            newErrors.standbyEndpoint = 'Standby 엔드포인트는 az-a 또는 az-b로 시작해야 합니다.';
        } else {
            const standbyParts = standbyEndpoint.split('.');
            if (standbyParts.length < 6 || (standbyParts[0] !== 'az-a' && standbyParts[0] !== 'az-b')) {
                isValid = false;
                newErrors.standbyEndpoint = 'Standby 엔드포인트 형식이 유효하지 않습니다.';
            } else if (!/^[0-9a-f]{32}$/.test(standbyParts[2])) {
                isValid = false;
                newErrors.standbyEndpoint = 'Standby 엔드포인트의 UUID 형식이 유효하지 않습니다.';
            } else if (standbyParts.slice(3).join('.') !== 'mysql.managed-service.kr-central-2.kakaocloud.com') {
                isValid = false;
                newErrors.standbyEndpoint = 'Standby 엔드포인트는 "mysql.managed-service.kr-central-2.kakaocloud.com"로 끝나야 합니다.';
            }
        }

        // az-a와 az-b의 상호 검증
        if (primaryEndpoint.startsWith('az-a') && !standbyEndpoint.startsWith('az-b')) {
            isValid = false;
            newErrors.standbyEndpoint = 'Primary 엔드포인트가 az-a로 시작하면 Standby 엔드포인트는 az-b로 시작해야 합니다.';
        } else if (primaryEndpoint.startsWith('az-b') && !standbyEndpoint.startsWith('az-a')) {
            isValid = false;
            newErrors.standbyEndpoint = 'Primary 엔드포인트가 az-b로 시작하면 Standby 엔드포인트는 az-a로 시작해야 합니다.';
        }

        setErrors(newErrors);
        return isValid;
    };

    const generateScript = async () => {
        if (validateForm()) {
            const newScript = `#!/bin/bash
echo "kakaocloud: 1.Starting environment variable setup"

# 환경 변수 설정: 사용자는 이 부분에 자신의 환경에 맞는 값을 입력해야 합니다.
command=$(cat <<EOF
export ACCESS_KEY="${accessKey}"
export SECRET_KEY="${secretKey}"
export PROJECT_NAME="${projectName}"
export CLUSTER_NAME="${clusterName}"
export API_ENDPOINT="${apiEndpoint}"
export AUTH_DATA="${authData}"
export INSTANCE_LIST="${instanceList}"
export PRIMARY_ENDPOINT="${primaryEndpoint}"
export STANDBY_ENDPOINT="${standbyEndpoint}"
export DOCKER_IMAGE_NAME="${dockerImageName}"
export DOCKER_JAVA_VERSION="${dockerJavaVersion}"
EOF
)

eval "$command"
echo "$command" >> /home/ubuntu/.bashrc
echo "kakaocloud: Environment variable setup completed"

echo "kakaocloud: 2.Checking the validity of the script download site"
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/script/script.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }

echo "kakaocloud: Script download site is valid"
wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/script/script.sh
chmod +x script.sh
sudo -E ./script.sh`;

            setScript(newScript);

            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    await navigator.clipboard.writeText(newScript);
                    alert('스크립트가 생성되고 클립보드에 복사되었습니다.');
                } else {
                    const textArea = document.createElement('textarea');
                    textArea.value = newScript;
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    try {
                        document.execCommand('copy');
                        alert('스크립트가 생성되고 클립보드에 복사되었습니다.');
                    } catch (err) {
                        console.error('클립보드에 복사하는 동안 오류가 발생했습니다:', err);
                    }
                    document.body.removeChild(textArea);
                }
            } catch (err) {
                console.error('클립보드에 복사하는 동안 오류가 발생했습니다:', err);
            }
        } else {
            alert('각 필드의 유효성을 체크해주세요.');
        }
    };

    const fetchProjects = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/get-project-name`, {
                access_key_id: accessKey,
                access_key_secret: secretKey,
            });
            const projectName = response.data.project_name;
            setProjectName(projectName);
        } catch (error) {
            console.error('API 호출 오류:', error);
        }
        setLoading(false);
    };

    const fetchClusters = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/get-clusters`, {
                access_key_id: accessKey,
                access_key_secret: secretKey,
            });
            const clusterNames = response.data.items.map((item: any) => item.name);
            setClusterList(clusterNames);
        } catch (error) {
            console.error('API 호출 오류:', error);
        }
        setLoading(false);
    };

    const fetchInstanceLists = async () => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/get-instance-groups`, {
                access_key_id: accessKey,
                access_key_secret: secretKey,
            });
            const instanceSetNames = response.data;
            setInstanceList(instanceSetNames.join(', '));
        } catch (error) {
            console.error('API 호출 오류:', error);
        }
        setLoading(false);
    };

    const fetchInstanceEndpoints = async (selectedInstanceName?: string) => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/get-instance-endpoints`, {
                access_key_id: accessKey,
                access_key_secret: secretKey,
                instance_set_name: selectedInstanceName
            });
            console.log('전체 응답 데이터:', response.data);
            const { primary_endpoint, standby_endpoint } = response.data;
            setInstanceEndpoints(prev => ({
                ...prev,
                [selectedInstanceName as string]: { primary_endpoint, standby_endpoint }
            }));
            setPrimaryEndpoint(primary_endpoint);
            setStandbyEndpoint(standby_endpoint);
        } catch (error) {
            console.error('API 호출 오류:', error);
        }
        setLoading(false);
    };

    const fetchKubeConfig = async (selectedClusterName?: string) => {
        setLoading(true);
        try {
            const response = await axios.post(`${API_BASE_URL}/get-kubeconfig`, {
                access_key_id: accessKey,
                access_key_secret: secretKey,
                cluster_name: selectedClusterName
            });
            const { clusters } = response.data;
            const selectedCluster = clusters.find((cluster: any) => cluster.name === selectedClusterName);
            if (selectedCluster) {
                setClusterName(selectedCluster.name);
                setApiEndpoint(selectedCluster.cluster.server);
                setAuthData(selectedCluster.cluster["certificate-authority-data"]);
            }
        } catch (error) {
            console.error('API 호출 오류:', error);
        }
        setLoading(false);
    };

    return (
        <Container>
            <Title>Bastion VM 스크립트 생성</Title>
            <Subtitle>kakaocloud 교육용</Subtitle>
            
            <GroupContainer>
                <InputBox
                    label="1. 액세스 키"
                    placeholder="직접 입력"
                    value={accessKey}
                    onChange={(e) => setAccessKey(e.target.value)}
                    error={errors.accessKey}
                />
                <InputBox
                    label="2. 시크릿 키"
                    placeholder="직접 입력"
                    value={secretKey}
                    onChange={(e) => setSecretKey(e.target.value)}
                    error={errors.secretKey}
                />
                <InputBox
                    label="3. 프로젝트 이름"
                    placeholder="조회 버튼 클릭 시 자동 입력"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    showApiButton
                    onApiClick={() => handleApiButtonClick('fetchProjects', handleFetchProjectsAndClusters)}
                    isLoading={loadingButton === 'fetchProjects'}
                    error={errors.projectName}
                />
            </GroupContainer>

            <GroupContainer>
                <SelectBox
                    label="4. 클러스터 이름"
                    value={clusterName}
                    options={clusterList}
                    onChange={handleClusterNameChange}
                />
                <InputBox
                    label="5. API 엔드포인트"
                    placeholder="위에서 클러스터 선택 시 자동 입력"
                    value={apiEndpoint}
                    onChange={(e) => setApiEndpoint(e.target.value)}
                    height="100px"
                    error={errors.apiEndpoint}
                />
                <InputBox
                    label="6. 인증 데이터"
                    placeholder="위에서 클러스터 선택 시 자동 입력"
                    value={authData}
                    onChange={(e) => setAuthData(e.target.value)}
                    height="100px"
                    error={errors.authData}
                />
            </GroupContainer>

            <GroupContainer>
                <InputBox
                    label="7. 인스턴스 목록"
                    placeholder="조회 버튼 클릭 시 자동 입력"
                    value={instanceList}
                    onChange={(e) => setInstanceList(e.target.value)}
                />
                <SelectBox
                    label="8. 인스턴스 이름"
                    value={instanceName}
                    options={instanceList.split(', ').filter(name => name.trim() !== '')}
                    onChange={handleInstanceNameChange}
                />
                <InputBox
                    label="9. Primary 엔드포인트"
                    placeholder="위에서 인스턴스 선택 시 자동 입력"
                    value={primaryEndpoint}
                    onChange={(e) => setPrimaryEndpoint(e.target.value)}
                    height="100px"
                    error={errors.primaryEndpoint}
                />
                <InputBox
                    label="10. Standby 엔드포인트"
                    placeholder="위에서 인스턴스 선택 시 자동 입력"
                    value={standbyEndpoint}
                    onChange={(e) => setStandbyEndpoint(e.target.value)}
                    height="100px"
                    isLoading={loadingButton === 'fetchInstanceStandbyEndpoints'}
                    error={errors.standbyEndpoint}
                />
            </GroupContainer>

            <GroupContainer>
                <InputBox
                    label="11. Docker 이미지명"
                    placeholder="예: demo-spring-boot"
                    value={dockerImageName}
                    onChange={(e) => setDockerImageName(e.target.value)}
                    error={errors.dockerImageName}
                />
                <InputBox
                    label="12. Java 버전"
                    placeholder="예: 17-jdk-slim"
                    value={dockerJavaVersion}
                    onChange={(e) => setDockerJavaVersion(e.target.value)}
                    error={errors.dockerJavaVersion}
                />
            </GroupContainer>

            <ScriptDisplay script={script} />
            
            <ButtonContainer>
                <StyledButton onClick={generateScript}>
                    스크립트 생성 및 복사
                </StyledButton>
            </ButtonContainer>
        </Container>
    );
};

export default MainPage;
