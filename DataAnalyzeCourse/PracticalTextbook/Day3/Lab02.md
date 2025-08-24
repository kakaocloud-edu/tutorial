# Kubeflow 생성

클러스터에 필수 및 선택 노드 풀을 설정하고, Kubeflow 소유자와 DB 설정, Object Storage를 Kubeflow 생성 및 구성하는 실습입니다.

## 1. Kubeflow 생성 (약 4~5분 소요)

1. 카카오 클라우드 콘솔 > AI Service > Kubeflow > Kubeflow
2. Kubeflow 서비스 시작하기 버튼 클릭
3. Kubeflow 생성 버튼 클릭
4. Kubeflow 기본 설정 정보 작성
    - Kubeflow 이름 : `kc-handson`
    - Kubeflow 구성
        - 버전 : `1.10`
        - 서비스 유형 : `체크된 기본값`
    - 클러스터 연결 : `k8s-cluster`
    - 클러스터 구성
        - Ingress 노드 풀 : `pool-ingress`
        - Worker 노드 풀 : `pool-worker`
        - CPU 노드 풀 (선택) : `pool-worker`
        - GPU 노드 풀 (선택) : `pool-gpu`
        - GPU MIG : `1g.10gb`
        - `+`를 눌러서 7을 선택
    - 기본 File Storage : `http://{File Storage IP}/handson(퍼블릭 액세스 허용)`
    - Object Storage 설정 : `Object Storage`
    - Kubeflow 소유자 설정
        - 소유자 이메일 계정 : `입력된 이메일로 임시 비밀번호 발송`
        - 네임스페이스 이름 : `kubeflow-tutorial`
        - 네임스페이스 파일 스토리지 : `http://{File Storage IP}/handson(퍼블릭 액세스 허용)`
    - DB 설정
        - DB 유형: `Kubeflow Internal DB`
        - 포트 : `3306`
        - 비밀번호 : `admin1234!`
        - 비밀번호 확인: `admin1234!`
    - 도메인 연결 (선택) : `빈 칸`
    - `생성` 버튼 클릭
5. `kc-handson` 생성 확인
6. 이메일로 전송된 임시 패스워드 복사 후 클립보드 등에 붙여넣기
    - **Note**: 추후 패스워드 변경 가능

## 2. Kubeflow 대시보드 접속

### 로드밸런서 Public IP를 이용

1. 카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
2. Kubeflow의 Ingress를 위해 생성된 두 개의 로드밸런서에 Public IP 연결
    - 로드밸런서 우측 더보기 버튼(점 3개) 클릭
    - `Public IP 연결` 클릭
    - `새로운 Public IP를 생성하고 자동으로 할당` 선택
    - `적용` 버튼 클릭
3. 부여된 Public IP 확인
4. 웹브라우저 주소창에 `http://{로드밸런서의 Public IP}` 입력하여 접속
5. 대시보드에 접속한 후 이메일 계정과 임시 패스워드를 사용하여 로그인
    - Email Address : `소유자 이메일 계정`
    - Password : `소유자 이메일로 전송된 임시 패스워드`
6. 로그인 확인
