import React from 'react';
import styled from 'styled-components';

const Button = styled.button`
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.75em 1.5em;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  transition: all 0.001s ease-in;
  margin: 0 1em;

  &:hover {
    background-color: #c82333;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 8px rgba(220, 53, 69, 0.6);
  }
`;

interface FormData {
  accessKey: string;
  secretKey: string;
  email: string;
  projectName: string;
  clusterName: string;
  apiEndpoint: string;
  authData: string;
  instanceList: string;
  primaryEndpoint: string;
  standbyEndpoint: string;
  dockerImageName: string;
  dockerJavaVersion: string;
}

interface ValidateButtonProps {
  formData: FormData;
  setErrors: React.Dispatch<React.SetStateAction<{ [key: string]: string }>>;
  clusterList: string[];
}

const ValidateButton: React.FC<ValidateButtonProps> = ({ formData, setErrors, clusterList = [] }) => {
  const validate = () => {
    const newErrors: { [key: string]: string } = {};
    let isValid = true;

    // 액세스 키 유효성 검사
    if (formData.accessKey.length < 32) {
      isValid = false;
      newErrors.accessKey = '액세스 키는 최소 32자리여야 합니다.';
    } else if (!/^[a-z0-9]+$/.test(formData.accessKey)) {
      isValid = false;
      newErrors.accessKey = '액세스 키는 소문자와 숫자로만 구성되어야 합니다.';
    }

    // 비밀 액세스 키 유효성 검사
    if (formData.secretKey.length < 64) {
      isValid = false;
      newErrors.secretKey = '비밀 액세스 키는 최소 64자리여야 합니다.';
    } else if (!/^[a-z0-9]+$/.test(formData.secretKey)) {
      isValid = false;
      newErrors.secretKey = '비밀 액세스 키는 소문자와 숫자로만 구성되어야 합니다.';
    }

    // // 이메일 유효성 검사
    // if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
    //   isValid = false;
    //   newErrors.email = '유효한 이메일 형식이 아닙니다.';
    // }

    // API 엔드포인트 유효성 검사
    const apiEndpointPattern = /^https:\/\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}-public\.ke\.kr-central-2\.kakaocloud\.com$/;
    if (!apiEndpointPattern.test(formData.apiEndpoint)) {
      isValid = false;
      newErrors.apiEndpoint = 'API 엔드포인트 형식이 유효하지 않습니다.';
    }

    // 인증 데이터 유효성 검사
    const authDataPattern = /^[A-Za-z0-9+/=]+$/;
    if (!authDataPattern.test(formData.authData)) {
      isValid = false;
      newErrors.authData = '인증 데이터는 유효한 Base64 형식이어야 합니다.';
    } else if (!formData.authData.endsWith('=')) {
      isValid = false;
      newErrors.authData = '인증 데이터는 "="로 끝나야 합니다.';
    } else {
      try {
        const decodedAuthData = atob(formData.authData);
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
    if (!/^[a-z]/.test(formData.projectName)) {
      isValid = false;
      newErrors.projectName = '프로젝트명은 영어 소문자로 시작해야 합니다.';
    } else if (!/^[a-z0-9-]+$/.test(formData.projectName)) {
      isValid = false;
      newErrors.projectName = '프로젝트명은 소문자, 숫자, "-"만 사용해야 합니다.';
    } else if (formData.projectName.length < 4 || formData.projectName.length > 30) {
      isValid = false;
      newErrors.projectName = '프로젝트명은 4~30자리여야 합니다.';
    }

    // Primary 엔드포인트 유효성 검사
    if (!formData.primaryEndpoint.startsWith('az-')) {
      isValid = false;
      newErrors.primaryEndpoint = 'Primary 엔드포인트는 az-a 또는 az-b로 시작해야 합니다.';
    } else {
      const primaryParts = formData.primaryEndpoint.split('.');
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
    if (!formData.standbyEndpoint.startsWith('az-')) {
      isValid = false;
      newErrors.standbyEndpoint = 'Standby 엔드포인트는 az-a 또는 az-b로 시작해야 합니다.';
    } else {
      const standbyParts = formData.standbyEndpoint.split('.');
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
    if (formData.primaryEndpoint.startsWith('az-a') && !formData.standbyEndpoint.startsWith('az-b')) {
      isValid = false;
      newErrors.standbyEndpoint = 'Primary 엔드포인트가 az-a로 시작하면 Standby 엔드포인트는 az-b로 시작해야 합니다.';
    } else if (formData.primaryEndpoint.startsWith('az-b') && !formData.standbyEndpoint.startsWith('az-a')) {
      isValid = false;
      newErrors.standbyEndpoint = 'Primary 엔드포인트가 az-b로 시작하면 Standby 엔드포인트는 az-a로 시작해야 합니다.';
    }

    // // Docker 이미지 이름 유효성 검사
    // if (formData.dockerImageName !== 'demo-spring-boot') {
    //   isValid = false;
    //   newErrors.dockerImageName = 'Docker 이미지 이름은 demo-spring-boot이어야 합니다.';
    // }
    //
    // // Docker Java 버전 유효성 검사
    // if (formData.dockerJavaVersion !== '17-jdk-slim') {
    //   isValid = false;
    //   newErrors.dockerJavaVersion = 'Docker Java 버전은 17-jdk-slim이어야 합니다.';
    // }

    setErrors(newErrors);

    if (isValid) {
      alert('모든 입력이 유효합니다.');
    } else {
      alert('입력에 오류가 있습니다. 각 필드를 확인하세요.');
    }
  };

  return <Button onClick={validate}>유효성 검사</Button>;
};

export default ValidateButton;
