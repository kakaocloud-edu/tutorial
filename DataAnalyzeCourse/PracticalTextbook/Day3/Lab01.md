# 실습 환경 구성
Kubeflow 실습을 위한 프로젝트 기본 환경 실습을 진행합니다. Kubernetes Engine, Node Pool, File Storage 등을 생성합니다.

## 1. Kubernetes Engine Cluster 생성 (약 10~15분 소요)
1. 카카오 클라우드 콘솔 > Container Pack > Kubernetes Engine > 클러스터
2. 클러스터 서비스 `시작하기` 버튼 클릭
3. `클러스터 생성` 클릭
4. 클러스터 기본 설정 정보 작성
    - 기본 설정
        - 클러스터 이름: `k8s-cluster`
        - 클러스터 설명(선택): `빈 칸`
        - Kubernetes 버전 : `1.31`
    - 클러스터 Network 설정
        - VPC : `kc-vpc`
        - Subnet : `main`, `public` 선택     
    - 클러스터 엔드포인트 액세스 : `퍼블릭 엔드포인트`
    - CNI
       - `Calico` 선택
       - 서비스 IP CIDR 블록(선택): 빈칸
       - 파드 IP CIDR 블록(선택): 빈칸
   - `생성` 버튼 클릭
5. 클러스터 생성 상태 확인 

## 2. Kubernetes Engine Cluster의 노드풀 생성
1. 생성된 `k8s-cluster` 클릭
2. 생성된 k8s-cluster 세부 정보 확인

#### pool-ingress 노드풀 생성 (약 3분 소요)
3. 노드 풀 탭 > `노드 풀 생성` 클릭
4. pool-ingress 노드 풀 설정 정보
    - 노드 풀 타입: `Virtual Machine`
    - 기본 설정
        - 노드 풀 이름: `pool-ingress`
        - 노드 풀 설명(선택): `빈 칸`
    - Image: `Ubuntu 22.04`
    - Instance 타입: `m2a.large`
    - Volume: SSD `50GB`
    - 노드 수: `1`
    - 노드 풀 Network 설정
        - VPC: `kc-vpc`
        - Subnet : `main`, `public` 선택 
    - 보안 그룹
        - `보안 그룹 생성` 버튼 클릭
            - 우측 상단의 `보안 그룹 생성` 버튼 클릭
                - 보안 그룹 이름: `clu-sg`
                - 인바운드 규칙
                    - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `6443`, 설명(선택): `kubernetes`
                - 아웃바운드 규칙
                    - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
                - `생성` 버튼 클릭
    - Key Pair: `keypair`
    - 고급 설정(선택): `빈 칸`
    - `생성` 버튼 클릭

#### pool-worker 노드풀 생성 (약 3분 소요) 
5. 노드 풀 탭 > 노드 풀 생성 클릭
6. pool-worker 노드 설정 정보
    - 노드 풀 타입: `Virtual Machine`
    - 기본 설정
        - 노드 풀 이름: `pool-worker`
        - 노드 풀 설명(선택): `빈 칸`
    - Image: `Ubuntu 22.04`
    - Instance 타입: `m2a.xlarge`
    - Volume: SSD `100GB`
    - 노드 수: `6`
    - 노드 풀 Network 설정
        - VPC: `kc-vpc`
        - Subnet : `main`, `public` 선택 
    - 보안 그룹
        - `보안 그룹 생성` 버튼 클릭
            - 우측 상단의 `보안 그룹 생성` 버튼 클릭
                - 보안 그룹 이름: `clu-sg`
                - 인바운드 규칙
                    - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `6443`, 설명(선택): `kubernetes`
                - 아웃바운드 규칙
                    - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
                - `생성` 버튼 클릭
    - Key Pair: `keypair`
    - 고급 설정(선택): `빈 칸`
    - `생성` 버튼 클릭

#### pool-gpu 노드풀 생성 (약 3분 소요)
7. 노드 풀 탭 > 노드 풀 생성성 클릭
8. pool-worker 노드 설정 정보
    - 노드 풀 타입: `GPU`
    - 기본 설정
        - 노드 풀 이름: `pool-gpu`
        - 노드 풀 설명(선택): 빈칸
    - Image: `Ubuntu 22.04`
    - Instance 타입: `p2i.6xlarge`
    - Volume: SSD `50GB`
    - 노드 수: `1`
    - 노드 풀 Network 설정
        - VPC: `kc-vpc`
        - Subnet : `main`, `public` 선택 
    - 보안 그룹
        - `보안 그룹 생성` 버튼 클릭
            - 우측 상단의 `보안 그룹 생성` 버튼 클릭
                - 보안 그룹 이름: `clu-sg`
                - 인바운드 규칙
                    - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `6443`, 설명(선택): `kubernetes`
                - 아웃바운드 규칙
                    - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
                - `생성` 버튼 클릭
    - Key Pair: `keypair`
    - 고급 설정(선택): `빈 칸`
    - `생성` 버튼 클릭
9. 노드 풀 탭에서 생성된 노드 풀 목록 확인
    - pool-ingress, pool-worker, pool-gpu 생성 확인
10. 노드 탭 클릭 후 노드 8개 생성 확인

## 3. 파일 스토리지 인스턴스 생성 (약 3분 소요)
1. 카카오 클라우드 콘솔 > Beyond Storage Service > File Storage > 인스턴스
2. 인스턴스 탭 > `인스턴스 생성` 클릭
3. 파일 인스턴스 설정 정보 작성
    - 인스턴스 정보
        - 인스턴스 이름: `kc-handson-fs`
        - 인스턴스 설명(선택): `빈 칸`
    - 프로토콜: `NFS`
    - 유형: `Basic`
    - 크기: `1TB`
    - 네트워크 설정
        - VPC : `kc-vpc`
        - 서브넷 : `main`
    - 접근 제어 설정: `설정된 VPC와 통신이 가능한 모든 프라이빗 IP 주소를 허용합니다.` 선택
    - 마운트 정보 설정 : `handson`
    - `생성` 클릭
