# Kubeflow 생성
클러스터에 필수 및 선택 노드 풀을 설정하고, Kubeflow 소유자와 DB 설정, Object Storage를 Kubeflow 생성 및 구성하는 실습입니다. 도메인 연결을 통해 외부 접근을 설정할 수 있습니다. 배포된 Kubeflow 환경에 접속하기 위하여 대시보드에 접속하는 실습입니다. 사용자는 대시보드를 통해 Kubeflow의 다양한 리소스를 관리하고, Jupyter Notebook 환경을 구성할 수 있습니다.

## 1. Kubeflow 생성 (약 4~5분 소요)
1. 카카오 클라우드 콘솔 > AI Service > Kubeflow > Kubeflow
2. Kubeflow 서비스 `시작하기` 버튼 클릭
3. Kubeflow 탭 > `Kubeflow 만들기` 버튼 클릭
4. 기본 설정 정보 작성
    - Kubeflow 이름 : `kc-handson`
    - Kubeflow 구성
        - 버전 : `1.0.0`
        - 서비스 타입 : `체크된 기본값`
    - 클러스터 연결 : `k8s-cluster`
    - 클러스터 구성
        - 필수 노드 풀 설정 
            - Ingress 노드 풀 : `pool-ingress`
            - Worker 노드 풀 : `pool-worker`
     - 선택 노드 풀 설정
         - CPU 노트북 노드 풀 : `pool-worker`
         - CPU 파이프라인 노드 풀 : `pool-worker`
         - GPU 노트북 노드 풀 : `pool-gpu`
         - GPU MIG : `1g.10gb`
             - `+`를 눌러서 7을 선택
         - GPU 파이프라인 노드 풀 : `pool-gpu`
     - 디폴트 파일 스토리지 : `handson`
     - Kubeflow 소유자 설정
         - 소유자 이메일 계정 : `입력된 이메일로 임시 비밀번호 발송`
         - 네임 스페이스 이름 : `kubeflow-tutorial`
         - 네임스페이스 파일 스토리지 : `http://172.16.2.116/handson(퍼블릭 액세스 허용)`
     - DB 설정
         - 포트 : `3306`
         - 비밀번호 : `admin1234!`
     - Object storage 타입 : `KC Object Storage`
     - [Demo] 도메인 연결 : kakaocloud-edu.com
     - `만들기` 버튼 클릭
5. Active 생성 확인
6. Kubeflow 생성 시 입력한 소유자 이메일 계정, 해당 이메일로 전송된 임시 비밀번호 복사 후 메모장에 붙여넣기
    - **Note**: 추후 비밀번호 변경 가능

## 2. Kubeflow 대시보드에 접속하기
### 로드밸런서 Public IP를 이용
1. 카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
2. Kubeflow의 Ingress를 위해 생성된 **두 개**의 로드밸런서(kube_service_{프로젝트 아이디}_{IKE 클러스터명}_ingress-nginx_ingress-nginx-controller)에 Public IP 연결
    - 로드밸런서 우측 더보기 버튼(점 3개) 클릭
    - `Public IP 연결` 클릭
    - `새로운 Public IP를 생성하고 자동으로 할당` 선택
    - `적용` 버튼 클릭
    - 새로 고침으로 할단된 Public IP 확인
3. 웹브라우저 주소창에 `http://{로드밸런서의 Public IP}` 입력하여 접속
4. 대시보드에 접속한 후 Kubeflow 생성 단계에서 입력한 소유자 이메일 계정과 복사해둔 소유자 이메일로 전송된 초기 패스워드를 사용하여 로그인
    - Email Address : `소유자 이메일 계정`
    - Password : `소유자 이메일로 전송된 초기 패스워드`
    - 로그인 확인

### Kubectl 포트 포워딩을 이용 (Demo)
1. 사용자 로컬 시스템의 특정 포트(예:8080)를 Kubeflow 대시보드 포트로 포워딩
    #### **lab2-3-1**
    - **Note**: 터미널에 입력해주세요
    ```
    kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80 --address 0.0.0.0
    ```
    - 포트 포워딩: 원격 서버의 특정 포트(e.g. 80)를 내 컴퓨터의 포트(e.g. 8080)로 연결
    - istio-ingressgateway: Istio의 외부 진입점으로서 클러스터 외부에서 들어오는 트래픽(일반적으로 HTTP, HTTPS)을 받아서 내부 서비스로 전달
2. 브라우저에서 로컬 호스트 8080 포트로 접속
   #### **lab2-3-2**
   - **Note**: 주소창에 입력해주세요
    ```
    http://localhost:8080
    ```
4. 대시보드에 접속한 후 Kubeflow 생성 단계에서 입력한 소유자 이메일 계정과 복사해둔 소유자 이메일로 전송된 초기 패스워드를 사용하여 로그인
    - Email Address : `소유자 이메일 계정`
    - Password : `소유자 이메일로 전송된 초기 패스워드`
    - 로그인 확인
