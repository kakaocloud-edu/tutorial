# 실습 환경 구성
Kubeflow 실습을 위한 프로젝트 기본 환경 실습을 진행합니다. VPC,  사용자 액세스 키 등을 생성합니다.

## 1. 조직 입력 및 로그인 (약 1분 소요)
- **Note**: 조직 관리자가 조직 구성원을 IAM 사용자로 조직 관리자가 사용자를 조직에 등록하면 해당 사용자의 이메일 주소로 조직 초대 및 비밀번호 등록 안내 메일이 발송
      
1. 사용자 이메일의 초대받은 메일을 통해 비밀번호 등록하기
    - 초기 비밀번호: `원하는 비밀번호`
        - 영어 대·소문자, 특수문자, 숫자 조합, 9~30자
    - 비밀번호 재입력: `초기 비밀번호에서 입력한 비밀번호와 동일한 비밀번호`
    - `비밀번호 등록하기` 버튼 클릭
3. 콘솔 로그인
    - 조직 이름: `kakaocloud-edu`
    - `다음` 클릭
    - 클라우드 계정: `사용자 이메일`
    - 비밀번호: `앞에서 등록한 비밀번호`
    - `콘솔 로그인` 버튼 클릭
4. 오른쪽 상단에 `kr-central-2` 리전 확인


## 2. IAM (약 1분 소요)
1. 카카오 클라우드 콘솔 > Management > IAM > 프로젝트 구성원
2. VPC 생성을 포함한 위 자원들의 생성을 위해 프로젝트 관리자(Admin) 권한이 부여됨을 확인

## 3.키 페어 준비
1. 카카오클라우드 콘솔 > Beyond Compute Service > Virtual Machine > 키 페어
2. 키 페어 탭에서 `키 페어 생성` 클릭
3. 신규 키 페어 설정 정보
    - 생성 방법: `신규 키 페어 생성하기` 선택
    - 이름: `keypair`
    - 유형 설정: `SSH`
    - `생성` 버튼 클릭

## 4. 액세스 키 준비 (약 1분 소요)
- **Note**: 사용자 액세스 키 만들기 팝업창을 닫은 이후 사용자 액세스 보안 키 정보 다시 조회 불가
- **Note**: 발급한 사용자 액세스 키를 콘솔에서 삭제할 경우 액세스 키는 자동 만료
- **Note**: 액세스 키를 일시적으로 정지 불가
1. 우측 상단 계정 프로필 > 액세스 키
2. 비밀번호 재확인
    - 클라우드 계정: `사용자 이메일`
    - 비밀번호: `비밀번호`
    - `비밀번호 확인` 버튼 클릭 
4. 사용자 액세스 키 탭 > `사용자 액세스 키 만들기` 클릭
5. 액세스 키 설정 정보
     - 사용자 액세스 키 이름 : `kakaocloud-test`
     - 프로젝트 지정 : `사용자가 위치한 프로젝트 지정`
     - 사용자 액세스 키 정보 : 빈칸
     - 만료 기한 : `지정하지 않음` 선택
     - `생성` 버튼 클릭
6. 사용자 액세스 키 ID, 사용자 액세스 보안 키 복사 후 메모장에 붙여넣기

## 5. [Demo] VPC 생성 (약 4~5분 소요)
1. 카카오 클라우드 콘솔 > Beyond Networking Service > VPC
2. VPC 탭 > `VPC 생성` 버튼 클릭
3. VPC 정보 작성
    - VPC 정보
        - VPC 이름 : `vpc_k8s`
        - VPC IP CIDR 블록 : `172.16.0.0/16`
    - Availability Zone
        - 가용 영역 개수 : `2`
        - 첫 번째 AZ : `kr-central-2-a`
        - 두 번째 AZ : `kr-central-2-b`
    - 서브넷 설정
        - AZ당 Public Subnet 개수 : `1`
        - AZ당 Private Subnet 개수 : `0`
        - kr-central2-a의 Public Subnet IPv4 CIDR 블록 : `172.16.0.0/20`
        - kr-central2-b의 Public Subnet IPv4 CIDR 블록 : `172.16.16.0/20`
    - 구성도 확인
    - `생성` 버튼 클릭
4. VPC 생성 상태 확인

## 6. Kubernetes Engine Cluster 생성 (약 10~15분 소요)
1. 카카오 클라우드 콘솔 > Container Pack > Kubernetes > Cluster
2. Cluster 서비스 `시작하기` 버튼 클릭
3. `클러스터 만들기` 클릭
4. 클러스터 기본 설정 정보 작성
    - 기본 설정
        - 클러스터 이름: `k8s-cluster`
        - 클러스터 설명(선택): 빈칸
        - Kubernetes 버전 : `1.27`
    - 클러스터 Network 설정
        - VPC : `vpc_k8s`
        - Subnet : `Public Subnet 2개 선택`
    - CNI
       - `Calico` 선택
       - 서비스 IP CIDR 블록(선택): 빈칸
       - 파드 IP CIDR 블록(선택): 빈칸
   - `만들기` 버튼 클릭
5. 클러스터 생성 상태 확인 

## 7. Kubernetes Engine Cluster의 노드풀 생성
1. 생성된 `k8s-cluster` 클릭
2. 생성된 k8s-cluster 세부 정보 확인

#### pool-ingress 노드풀 생성 (약 3분 소요)
3. 노드 풀 탭 > `노드 풀 만들기` 클릭
4. pool-ingress 노드 풀 설정 정보
    - 노드 풀 타입: `Virtual Machine`
    - 기본 설정
        - 노드 풀 이름: `pool-ingress`
        - 노드 풀 설명(선택): 빈칸
    - Image: `Ubuntu 20.04`
    - Instance 타입: `m2a.large`
    - Volume: SSD `50GB`
    - 노드 수: `1`
    - 노드 풀 Network 설정
        - VPC: `vpc_k8s`
        - Subnet: `Public 서브넷 2개` 선택
    - 리소스 기반 오토 스케일 (선택): `미사용`
    - Key Pair: `keypair`
    - 고급 설정(선택): 빈칸
    - `만들기` 버튼 클릭

#### pool-worker 노드풀 생성 (약 3분 소요) 
5. 노드 풀 탭 > 노드 풀 만들기 클릭
6. pool-worker 노드 설정 정보
    - 노드 풀 타입: `Virtual Machine`
    - 기본 설정
        - 노드 풀 이름: `pool-worker`
        - 노드 풀 설명(선택): 빈칸
    - Image: `Ubuntu 20.04`
    - Instance 타입: `m2a.xlarge`
    - Volume: SSD `100GB`
    - 노드 수: `6`
    - 노드 풀 Network 설정
        - VPC: `vpc_k8s`
        - Subnet: `Public 서브넷 2개` 선택
    - 리소스 기반 오토 스케일 (선택): `미사용`
    - Key Pair: `keypair`
    - 고급 설정(선택): 빈칸
    - `만들기` 버튼 클릭

#### pool-gpu 노드풀 생성 (약 3분 소요)
7. 노드 풀 탭 > 노드 풀 만들기 클릭
8. pool-worker 노드 설정 정보
    - 노드 풀 타입: `GPU`
    - 기본 설정
        - 노드 풀 이름: `pool-gpu`
        - 노드 풀 설명(선택): 빈칸
    - Image: `Ubuntu 20.04`
    - Instance 타입: `p2i.6xlarge`
    - Volume: SSD `50GB`
    - 노드 수: `1`
    - 노드 풀 Network 설정
        - VPC: `vpc_k8s`
        - Subnet: `Public 서브넷 2개` 선택
    - 리소스 기반 오토 스케일 (선택): `미사용`
    - Key Pair: `keypair`
    - 고급 설정(선택): 빈칸
    - `만들기` 버튼 클릭
9. 노드 풀 탭에서 생성된 노드 풀 목록 확인
    - pool-ingress, pool-worker, pool-gpu 생성 확인
10. 노드 탭 클릭 후 노드 8개 생성 확인
 

## 8. 파일 스토리지 인스턴스 생성 (약 3분 소요)
1. 카카오 클라우드 콘솔 > Beyond Storage Service > File Storage > 인스턴스
2. 인스턴스 탭 > `인스턴스 생성` 클릭
3. 파일 인스턴스 설정 정보 작성
    - 인스턴스 정보
        - 인스턴스 이름: `kc-handson-fs`
        - 인스턴스 설명(선택): 빈칸
    - 프로토콜: `NFS`
    - 유형: `Basic`
    - 크기: `1TB`
    - 네트워크 설정
        - VPC : `vpc_k8s`
        - 서브넷 : `main`
    - 접근 제어 설정: `설정된 VPC와 통신이 가능한 모든 프라이빗 IP 주소를 허용합니다.` 선택
    - 마운트 정보 설정 : `handson`
    - `생성` 클릭
