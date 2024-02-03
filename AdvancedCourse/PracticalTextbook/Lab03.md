# K8s engine Cluster 관리 VM 생성 실습

클러스터를 관리하기 위한 Bation VM 인스턴스를 생성하는 실습입니다.

## 1. Bastion VM 인스턴스 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Kubernetes Engine 접속
2. 클러스터 `kakao-k8s-cluster` 클릭
  - 서버 엔드 포인트 복사
3. kubectl 버튼 클릭
  - kubeconfig 파일 다운로드 클릭
    - kubeconfig 파일 열기
    - certificate-authority-data 값 복사

4. 스크립트를 메모장에 복사후 복사해놓은 값들을 입력하기
   #### **lab3-1-4**
     ```bash
     chmod 400 keyPair.pem
     ```

6. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
7. Instance 만들기 클릭
   - 이름 : `bastion`
   - Image : `Ubuntu 20.04`
   - Instance 타입 : `m2a.large`
   - Volume : `10 GB`
8. Key Pair : `keypair`
9. VPC 선택
    - VPC : `vpc_1`
    - Subnet : `main`
    - SecurityGroup 선택
10. 새 Security Group 생성 클릭
    - Security Group 이름: `bastion`
    - Inbound :
      - 프로토콜: `TCP`
      - 패킷 출발지: `{사용자 IP}/32`
        - **Note**: "사용자\_IP" 부분을 실제 IP 주소로 교체하세요.
          - 사용자 IP 조회: [https://www.myip.com/](https://www.myip.com/)
        - 실습 환경에 따라 사용자의 IP가 변경될 가능성이 있다면 `0.0.0.0/0` 으로 설정
      - 포트 번호: `22`
      - 프로토콜: `TCP`
      - 패킷 출발지: `0.0.0.0/32`
      - 포트 번호: `8080`
11. Outbound 클릭
    - Outbound
      - 프로토콜 : `ALL`
      - 패킷 목적지 : `0.0.0.0/0`
    - 만들기 버튼 클릭
12. 고급설정 버튼 클릭
    - 사용자 스크립트에 - **lab3-1-4** 내용을 붙여넣기
    - **Note**: 고급 설정 스크립트 부분을 못하더라도 추후 설정할 수 있습니다.
13. 만들기 버튼 클릭
14. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
15. 생성된 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
    - `새로운 Public IP를 생성하고 자동으로 할당` 
16. 확인 버튼 클릭
17. 생성된 인스턴스의 우측 메뉴바 > SSH 연결 클릭
     - SSH 접속 명령어 복사(다운받은 keyPair.pem 파일이 있는 경로에서 아래 명령어를 실행합니다.)
     - 터미널 열기
     - Keypair를 다운받아놓은 폴더로 이동
     - 터미널에 명령어 붙여넣기
     - yes 입력
    #### **lab3-1-16-1**
     ```bash
     cd {keypair.pem 다운로드 위치}
     ```
     - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정

     #### **lab3-1-16-2**
     ```bash
     chmod 400 keyPair.pem
     ```

     #### **lab3-1-16-3**
     ```bash
     ssh -i keyPair.pem centos@{bastion의 public ip주소}
     ```
     - **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.
   
     #### **lab3-1-16-4**
     ```bash
     yes
     ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keyPair.pem가 있는 경로로 이동 후 아래 명령어 입력
     #### **lab3-1-16-5**
     ```bash
     icacls.exe keyPair.pem /reset
     icacls.exe keyPair.pem /grant:r %username%:(R)
     icacls.exe keyPair.pem /inheritance:r
     ```

## 2. Bastion VM 인스턴스를 통해 클러스터 확인


1. 클러스터 확인 명령어
    #### **lab3-2-1**
     ```bash
     kubectl get nodes
     ```
2. 두 개의 노드가 정상적으로 나오는지 확인
