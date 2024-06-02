실습 환경 구성
===
kubeflow 실습을 위한 프로젝트 실습 환경구성입니다.

## 1. 조직 입력 및 로그인
본 실습에서는 ‘가비아’ 라는 도메인 제공 서비스를 이용

## 2. IAM
1. 카카오 클라우드 콘솔 > 서비스 > Management > IAM > 프로젝트 구성원
2. 프로젝트 관리자(Admin) 권한이 부여됨을 확인

## 3. VM 접근용 키 페어 준비
1. 카카오클라우드 콘솔 > 서비스 > Beyond Compute Service > Virtual Machine > 키 페어
2. 키 페어 탭에서 '키 페어 생성' 버튼 클릭
    - `신규 키 페어 생성하기` 선택
    - 이름: `keypair`
    - 유형: `SSH`
3. '생성' 버튼 클릭

## 4. 액세스 키 준비

1. 우측 상단 계정 프로필 > 사용자 액세스 키 > 비밀번호 확인
2. `사용자 액세스 키 만들기` 클릭
     - 사용자 액세스 키 이름 : `kakaocloud-test`
     - 프로젝트 지정 : `사용자가 위치한 프로젝트 지정`
     - 사용자 액세스 키 정보 : `사용자 선택 입력`
     - 만료 기한 : `지정하지 않음`
3. `생성` 버튼 클릭
5. 사용자 액세스 키 ID 복사 후 메모장에 붙여넣기
6. 사용자 액세스 보안 키 복사 후 메모장에 붙여넣기
  - **Note**: 사용자 액세스 키 만들기 팝업창을 닫은 이후 사용자 액세스 보안 키 정보 다시 조회 불가
  - **Note**: 나중에 스크립에 작성 시 사용
## 5. VPC 생성 (데모)
1. 카카오 클라우드 콘솔 > 서비스 > Beyond Networking Service > VPC
2. `+VPC 생성` 클릭
   - VPC 정보
     - VPC 이름 : `vpc_k8s`
     - VPC IP CIDR 블록 : 172.16.0.0/16
        - Availability Zone
     - AZ 개수 : `2`
     - 첫 번째 AZ : `kr-central-2-a`
     - 두 번째 AZ : `kr-central-2-b`
   - Subnet 설정
     - AZ당 Public Subnet 개수 : `1`
     - AZ당 Private Subnet 개수 : `0`
     - kr-central2-a의 Public Subnet IPv4 CIDR 블록 : `172.16.0.0/20`
     - kr-central2-b의 Public Subnet IPv4 CIDR 블록 : `172.16.16.0/20`
3. `생성` 클릭
4. VPC 생성 확인

## 6. Kubernetes Engine Cluster 생성
1. 카카오 클라우드 콘솔 > 서비스 > Container Pack > Kubernetes > Cluster
2. `시작하기` 클릭
3. `+클러스터 만들기` 클릭
   - 쿠버네티스 설정 정보
     - 클러스터 설정 : `k8s-cluster`
     - Kubernetes 버전 : `1.27`
     - 클러스터 Network 설정
     - VPC : `vpc_k8s`
     - Subnet : `Public Subnet 2개 선택`
     - CN 설정
       - `Calico` 선택
       - 기본설정 : `공백`
5. `만들기` 클릭

## 7. Kubernetes Engine Cluster의 노드풀 생성
1. 생성된 `kakao-k8s` 클릭
2. 생성된 `kakao-k8s` 세부 정보 확인

#### pool-ingress 노드
4. `노드 풀` > `노드 풀 만들기` 클릭
   - pool-ingress 노드 설정 정보
       - 노드 풀 타입 : `Virtual Machine`
       - 기본 설정
         - 노드 풀 이름 : `pool-ingress`
         - Image 선택 : `Ubuntu 20.04`
         - Instance 타입 : `m2a.large`
         - Volume 크기 : `50GB`
         - 노드 수 : `2`
       - 노드 풀 Network 설정
         - VPC : `vpc_k8s` 선택
         - Subnet : `Public 서브넷`들만 선택
       - 자동 확장 설정 : `사용 안함`
       - key Pair
         - 이름 : `kakaocloud-test`
6. 고급 설정 생략 후 `만들기` 버튼 클릭

#### pool-worker 노드
5. `노드 풀` > `노드 풀 만들기` 클릭
   - pool-worker 노드 설정 정보
       - 노드 풀 타입 : `Virtual Machine`
       - 기본 설정
         - 노드 풀 이름 : `pool-worker`
         - Image 선택 : `Ubuntu 20.04`
         - Instance 타입 : `m2a.xlarge`
         - Volume 크기 : `100GB`
         - 노드 수 : `6`
       - 노드 풀 Network 설정
         - VPC : `vpc_k8s` 선택
         - Subnet : `Public 서브넷`들만 선택
       - 자동 확장 설정 : `사용 안함`
       - key Pair
         - 이름 : `kakaocloud-test`
7. 고급 설정 생략 후 `만들기` 버튼 클릭

#### pool-gpu 노드
7.  `노드 풀` > `노드 풀 만들기` 클릭
   - #### pool-gpu 노드 설정 정보
       - 노드 풀 타입 : `GPU`
       - 기본 설정
         - 노드 풀 이름 : `pool-gpu`
         - Image 선택 : `Ubuntu 20.04`
         - Instance 타입 : `p2i.6xlarge`
         - Volume 크기 : `50GB`
         - 노드 수 : `1`
       - 노드 풀 Network 설정
         - VPC : `vpc_k8s` 선택
         - Subnet : `Public 서브넷`들만 선택
       - 자동 확장 설정 : `사용 안함`
       - key Pair
         - 이름 : `kakaocloud-test`
8. 고급 설정 생략 후 `만들기` 버튼 클릭
9. 생성된 노드 풀 확인

## 8. 파일 스토리지 인스턴스 생성
1. 카카오 클라우드 콘솔 > 서비스 > Beyond Storage Service > File Storage > 인스턴스
2. 인스턴스 탭 > `인스턴스 생성` 클릭
  - 파일 인스턴스 설정 정보
    - 이름 : `kc-handson-fs`
    - 볼륨 크기 : `1TB`
    - VPC : `vpc_k8s`
    - 서브넷 : `main`
    - 접근 제어 설정 : `설정된 VPC와 통신이 가능한 모든 프라이빗 IP 주소를 허용합니다.`
    - 마운트 정보 설정 : `handson`
3. `만들기` 클릭
4. `Active` 상태 확인
