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
     
    # 환경 변수 설정. 여기 부분만 값을 입력해주세요.
    export PROJECT_NAME_USER="프로젝트 이름 입력"
    
    export ACC_KEY="사용자 액세스 키 ID 입력"
    export SEC_KEY="사용자 액세스 보안 키 입력"
    
    export CLUSTER_NAME="클러스터 이름 입력"
    export API_SERVER="클러스터의 API 엔드포인트 입력"
    export AUTH_DATA="클러스터의 certificate-authority-data 입력"
    
    export INPUT_DB_EP1="데이터베이스 1의 엔드포인트 입력"
    export INPUT_DB_EP2="데이터베이스 2의 엔드포인트 입력"
    
    # 이미지 이름 : demo-spring-boot
    export IMAGE_NAME_USER="이미지 이름 입력"
    
    # 자바 버전 : 17-jdk-slim
    export JAVA_VERSION_USER="자바 버전 입력"
    
    
    # 여기부터는 값을 변경하시면 안됩니다.
    DB_EP1=$(echo -n "$INPUT_DB_EP1" | base64 -w 0)
    DB_EP2=$(echo -n "$INPUT_DB_EP2" | base64 -w 0)
    
    tee -a /etc/environment << EOF
    export JAVA_VERSION="17"
    export SPRING_BOOT_VERSION="3.1.0"
    export DOCKER_IMAGE_NAME="${IMAGE_NAME_USER}"
    export DOCKER_JAVA_VERSION="${JAVA_VERSION_USER}"
    export PROJECT_NAME="${PROJECT_NAME_USER}"
    EOF
    
    source /etc/environment
    
    mkdir /home/ubuntu/yaml
    chmod 777 /home/ubuntu/yaml
    wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/lab6Yaml.tar -O /home/ubuntu/yaml/lab6Yaml.tar
    
    cat <<EOF > /home/ubuntu/yaml/lab6-Secret.yaml
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
    
    cat <<EOF > /home/ubuntu/yaml/lab6-Deployment.yaml
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
        spec:
          affinity:
            podAntiAffinity:
              preferredDuringSchedulingIgnoredDuringExecution:
                - weight: 100
                  podAffinityTerm:
                    labelSelector:
                      matchExpressions:
                        - key: app
                          operator: In
                          values:
                            - kc-spring-demo
                    topologyKey: kubernetes.io/hostname
          containers:
          - name: kc-webserver
            image: ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/${DOCKER_IMAGE_NAME}:1.0
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
    
    cat <<EOF > /home/ubuntu/yaml/lab6-ConfigMapDB.yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: sql-script
    data:
      script.sql: |
        CREATE DATABASE IF NOT EXISTS history;
        USE history;
        CREATE TABLE IF NOT EXISTS access (
          id INT AUTO_INCREMENT PRIMARY KEY,
          date VARCHAR(255) NOT NULL
        );
        INSERT INTO access (date) VALUES ('hello:)');
        CALL mysql.mnms_grant_right_user('admin', '%', 'all', '*', '*');
        ALTER USER 'admin'@'%' IDENTIFIED WITH mysql_native_password BY 'admin1234';
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
      name: ${CLUSTER_NAME}
    contexts:
    - context:
        cluster: ${CLUSTER_NAME}
        user: ${CLUSTER_NAME}-admin
      name: ${CLUSTER_NAME}-admin@${CLUSTER_NAME}
    current-context: ${CLUSTER_NAME}-admin@${CLUSTER_NAME}
    kind: Config
    preferences: {}
    users:
    - name: ${CLUSTER_NAME}-admin
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
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo chmod 666 /var/run/docker.sock
    
    sudo apt install unzip
    sudo apt-get install -y openjdk-17-jdk maven
    
    chmod 600 /home/ubuntu/.kube/config
    chown ubuntu:ubuntu /home/ubuntu/.kube/config
    
    cat <<EOF > /home/ubuntu/values.yaml
    
    replicaCount: 2
    
    deployment:
      repository: ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/${DOCKER_IMAGE_NAME}
      tag: "1.0"
      pullSecret: regcred
    
    service:
      type: ClusterIP
      port: 80
      targetPort: 8080
    
    ingress:
      enabled: true
      className: nginx
      path: /
      sslRedirect: "false"
    
    configMap:
      WELCOME_MESSAGE: "Welcome to Kakao Cloud"
      BACKGROUND_COLOR: "#4a69bd"
    
    secret:
      DB1_PORT: '3306'
      DB1_URL: '${INPUT_DB_EP1}'
      DB1_ID: 'admin'
      DB1_PW: 'admin1234'
      DB2_PORT: '3307'
      DB2_URL: '${INPUT_DB_EP2}'
      DB2_ID: 'admin'
      DB2_PW: 'admin1234'
    
    job:
      name: sql-job
      image: mysql:5.7
      scriptConfigMap: sql-script
      backoffLimit: 4
    
    hpa:
      enabled: false
      minReplicas: 2
      maxReplicas: 6
      averageUtilization: 50
    EOF
    ```
    
5. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
6. Instance 만들기 클릭
   - 이름 : `bastion`
   - Image : `Ubuntu 20.04 - 5.4.0-164`
   - Instance 타입 : `m2a.large`
   - Volume : `10 GB`
7. Key Pair : `keypair`
8. VPC 선택
    - VPC : `vpc_1`
    - Subnet : `main`
    - SecurityGroup 선택
9. 새 Security Group 생성 클릭
    - Security Group 이름: `bastion`
    - Inbound :
      - 프로토콜: `TCP`
      - 패킷 출발지: `{교육장의 사설 IP}/32`
        - **Note**: "교육장의 사설 IP" 부분을 실제 IP 주소로 교체하세요.
      - 포트 번호: `22`
      - 프로토콜: `TCP`
      - 패킷 출발지: `0.0.0.0/32`
      - 포트 번호: `8080`
10. Outbound 클릭
    - Outbound
      - 프로토콜 : `ALL`
      - 패킷 목적지 : `0.0.0.0/0`
    - 만들기 버튼 클릭
11. 고급설정 버튼 클릭
    - 사용자 스크립트에 **lab3-1-4** 내용을 붙여넣기
    - **Note**: 고급 설정 스크립트 부분을 못하더라도 추후 설정할 수 있습니다.
12. 만들기 버튼 클릭
13. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
14. 생성된 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
    - `새로운 Public IP를 생성하고 자동으로 할당` 
15. 확인 버튼 클릭
16. 생성된 인스턴스의 우측 메뉴바 > SSH 연결 클릭
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
17. bastion 생성 시에 고급 설정을 진행하지 않았을 때 진행
     #### **lab3-1-17-1**
     ```bash
     wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/script/script.sh
     ```

     #### **lab3-1-17-2**
     ```bash
     chmod +x script.sh
     ```

     #### **lab3-1-17-3**
     ```bash
     ./script.sh
     ```

     
## 2. Bastion VM 인스턴스를 통해 클러스터 확인


1. 클러스터 확인 명령어
    #### **lab3-2-1**
     ```bash
     kubectl get nodes
     ```
2. 두 개의 노드가 정상적으로 나오는지 확인
