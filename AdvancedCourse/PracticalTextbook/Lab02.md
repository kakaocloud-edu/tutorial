# Kubernetes Engine Cluster 생성

Kakao Cloud Kubernetes Engine Cluster 생성에 대한 실습입니다.

## 1. 클러스터 생성

1. 카카오 클라우드 콘솔 > Container Pack > Kubernetes > Cluster 접속
2. 시작하기 버튼 클릭
3. 클러스터 만들기 버튼 클릭
   - 기본 설정
     - 클러스터 이름 : `kakao-k8s-cluster`
     - kubernetes 버전 : `1.26`
   - 클러스터 Network 설정
     - VPC : `vpc_1`
     - Subnet : 모든 서브넷 선택
4. 만들기 버튼 클릭

## 2. 노드 풀 생성

1. 카카오 클라우드 콘솔 > Container Pack > Kubernetes > Cluster 접속
2. 생성된 클러스터 `kakao-k8s-cluster` 클릭
3. 노드 풀 클릭
4. 노드 풀 만들기 버튼 클릭
   - 노드 풀 타입 : `Virtual Machine`
   - 기본 설정
     - 노드 풀 이름 : `node-pool`
     - Image 선택 : `Ubuntu 20.04`
     - Instance 타입 : `m2a-large`
     - Volume 크기 : `50GB`
     - 노드 수 : `2`
   - 노드 풀 Network 설정
     - VPC : `vpc_1` 선택
     - Subnet : Public 서브넷들만 선택
   - 자동 확장 설정 : `사용 안함`
   - key Pair
     - 신규 Key Pair 생성 클릭
       - 이름 : `keypair`
       - 생성 및 다운로드 버튼 클릭
5. 고급 설정 생략 후 만들기 버튼 클릭
6. 카카오 클라우드 콘솔 > 전체 서비스 > Kubernetes Engine 접속
7. `kakao-k8s-cluster` 클릭
8. 노드 탭으로 이동
9. 노드 생성 여부 확인
