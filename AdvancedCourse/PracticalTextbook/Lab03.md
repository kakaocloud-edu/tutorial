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

5. 스크립트 환경변수 텍스트 파일에 복사하기
   #### **lab3-1-7**

  ```bash
  #!/bin/bash
  

  # 환경 변수 설정. 여기 부분만 값을 입력해주세요.
  export PROJECT_NAME="프로젝트 이름 입력"

  export ACC_KEY = "사용자 엑세스 키 아이디 입력"
  export SEC_KEY = "사용자 엑세스 시크릿 키 입력"

  export API_SERVER = "클러스터의 API 엔드포인트 입력"
  export AUTH_DATA = "클러스터의 AUTHORITY_DATA 입력"

  export INPUT_DB_EP1="데이터베이스 1의 엔드포인트 입력"
  export INPUT_DB_EP2="데이터베이스 2의 엔드포인트 입력"

  # 여기부터는 값을 변경하시면 안됩니다.
  DB_EP1=$(echo -n "$INPUT_DB_EP1" | tr -d ' ' | base64)
  DB_EP2=$(echo -n "$INPUT_DB_EP2" | tr -d ' ' | base64)

  cat <<EOF > /home/ubuntu/lab6-Secret.yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: app-secret
  type: Opaque
  data:
    DB1_PORT: 'MzMwNg=='
    DB1_URL: "${DB_EP1}"
    DB1_ID: 'YWRtaW4='
    DB1_PW: 'YWRtaW4xMjM0'
    DB2_PORT: 'MzMwNw=='
    DB2_URL: "${DB_EP2}"
    DB2_ID: 'YWRtaW4='
    DB2_PW: 'YWRtaW4xMjM0'
  EOF

  cat <<EOF > /home/ubuntu/lab6-Deployment.yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: demo-deployment
    labels:
      app: kc-spring-demo
  spec:
    replicas: 2  # 복제본 갯수
    selector:
      matchLabels:
        app: kc-spring-demo
    template:
      metadata:
        labels:
          app: kc-spring-demo
      spec:
        containers:
        - name: kc-webserver
          image: ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/demo-spring-boot:latest
          envFrom:
          - configMapRef:
              name: app-config
          - secretRef:
              name: app-secret
          ports:
          - containerPort: 8080
        imagePullSecrets:
        - name: regcred  # NCR에 저장된 이미지 Pulling을 위한 인증 Secret 값
  EOF

  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

  mkdir /home/ubuntu/.kube

  cat <<EOF > /home/ubuntu/.kube/config
  apiVersion: v1
  clusters:
  - cluster:
      certificate-authority-data: "${AUTH_DATA}"
      server: ${API_SERVER}
    name: kakao-k8s-cluster
  contexts:
  - context:
      cluster: kakao-k8s-cluster
      user: kakao-k8s-cluster-admin
    name: kakao-k8s-cluster-admin@kakao-k8s-cluster
  current-context: kakao-k8s-cluster-admin@kakao-k8s-cluster
  kind: Config
  preferences: {}
  users:
  - name: kakao-k8s-cluster-admin
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1beta1
        args: null
        command: kic-iam-auth
        env:
        - name: "OS_AUTH_URL"
          value: "https://iam.kakaoi.io/identity/v3"
        - name: "OS_AUTH_TYPE"
          value: "v3applicationcredential"
        - name: "OS_APPLICATION_CREDENTIAL_ID"
          value: "${ACC_KEY}"
        - name: "OS_APPLICATION_CREDENTIAL_SECRET"
          value: "${SEC_KEY}"
        - name: "OS_REGION_NAME"
          value: "kr-central-2"
  EOF

  wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O kic-iam-auth
  sudo chmod +x /kic-iam-auth
  sudo mv /kic-iam-auth /usr/local/bin

  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg —dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io
  sudo chmod 666 /var/run/docker.sock

  sudo apt install unzip
  sudo apt-get install -y openjdk-17-jdk maven

   sudo tee -a /etc/environment << EOF
   export API_SERVER="{lab3 1-3에서 복사한 서버 엔드 포인트}"
   export USER_ACCESS_KEY_ID="{사용자 엑세스 키 ID}"
   export USER_ACCESS_KEY_SECRET="{사용자 엑세스 보안 키}"
   export AUTHORITY_DATA="{lab3 1-6 복사한 certificate-authority-data 값}"
   EOF

   source /etc/environment

   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

   mkdir /home/ubuntu/.kube

   cat <<EOF > /home/ubuntu/.kube/config
   apiVersion: v1
   clusters:
   - cluster:
      certificate-authority-data: ${AUTHORITY_DATA}
      server: ${API_SERVER}
    name: kakao-k8s-cluster
   contexts:
   - context:
      cluster: kakao-k8s-cluster
      user: kakao-k8s-cluster-admin
    name: kakao-k8s-cluster-admin@kakao-k8s-cluster
   current-context: kakao-k8s-cluster-admin@kakao-k8s-cluster
   kind: Config
   preferences: {}
   users:
   - name: kakao-k8s-cluster-admin
    user:
      exec:
        apiVersion: client.authentication.k8s.io/v1beta1
        args: null
        command: kic-iam-auth
        env:
        - name: "OS_AUTH_URL"
          value: "https://iam.kakaoi.io/identity/v3"
        - name: "OS_AUTH_TYPE"
          value: "v3applicationcredential"
        - name: "OS_APPLICATION_CREDENTIAL_ID"
          value: "${USER_ACCESS_KEY_ID}"
        - name: "OS_APPLICATION_CREDENTIAL_SECRET"
          value: "${USER_ACCESS_KEY_SECRET}"
        - name: "OS_REGION_NAME"
          value: "kr-central-2"
   EOF

   wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O kic-iam-auth
   sudo chmod +x /kic-iam-auth
   sudo mv /kic-iam-auth /usr/local/bin

   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
   echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io
   sudo chmod 666 /var/run/docker.sock

   sudo apt install unzip
   sudo apt-get install -y openjdk-17-jdk
   ```

8. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
9. Instance 만들기 클릭
   - 이름 : `bastion`
   - Image : `Ubuntu 20.04`
   - Instance 타입 : `m2a.large`
   - Volume : `10 GB`
10. Key Pair : `keypair`
11. VPC 선택
    - VPC : `vpc_1`
    - Subnet : `main`
    - SecurityGroup 선택
12. 새 Security Group 생성 클릭
    - Security Group 이름: `bastion`
    - Inbound :
      - 프로토콜: `TCP`
      - 패킷 출발지: `{사용자 IP}/32`
        - **Note**: "사용자\_IP" 부분을 실제 IP 주소로 교체하세요.
          - 사용자 IP 조회: [https://www.myip.com/](https://www.myip.com/)
        - 실습 환경에 따라 사용자의 IP가 변경될 가능성이 있다면 `0.0.0.0/0` 으로 설정
      - 포트 번호: `22`
13. Outbound 클릭
    - Outbound
      - 프로토콜 : `ALL`
      - 패킷 목적지 : `0.0.0.0/0`
    - 만들기 버튼 클릭
14. 고급설정 버튼 클릭
    - 사용자 스크립트에 - **lab3-1-7** 내용을 붙여넣기
    - **Note**: 고급 설정 스크립트 부분을 못하더라도 추후 설정할 수 있습니다.
15. 만들기 버튼 클릭
16. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
17. 생성된 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
    - `새로운 Public IP를 생성하고 자동으로 할당` 
18. 확인 버튼 클릭
19. 생성된 인스턴스의 우측 메뉴바 > SSH 연결 클릭
     - SSH 접속 명령어 복사(다운받은 keyPair.pem 파일이 있는 경로에서 아래 명령어를 실행합니다.)
     - 터미널 열기
     - Keypair를 다운받아놓은 폴더로 이동
     - 터미널에 명령어 붙여넣기
     - yes 입력
    #### **lab4-1-12-1**
     ```bash
     cd {keypair.pem 다운로드 위치}
     ```
     - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정

     #### **lab4-1-12-2**
     ```bash
     chmod 400 keyPair.pem
     ```

     #### **lab4-1-12-4**
     ```bash
     ssh -i keyPair.pem centos@{bastion의 public ip주소}
     ```
     - **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.
   
     #### **lab3-1-19**
     ```bash
     yes
     ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keyPair.pem가 있는 경로로 이동 후 아래 명령어 입력
     #### **lab4-1-12-3**
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
