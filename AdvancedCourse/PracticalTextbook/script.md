# bastion 스크립트 명령 실패 시 수동으로 명령어 입력



  ```bash
export PROJECT_NAME="kakaocloud-test"
export ACC_KEY="98cd807afa0c4555baa67cfeab039ec3"
export SEC_KEY="1j8zie-QAgZ4U5gRN9IXFFlD8W6AxcN563lZL943RGIs8Yj1cXK85IndQ_b3h2SqamJAz-7ENnjiNPjV5DCwwg"
export API_SERVER="https://9ce75b66-3314-42d7-89ff-c841b7f340f7-public.ke.kr-central-2.kakaocloud.com:443"
export AUTH_DATA="LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM2akNDQWRLZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJME1ESXdNVEV3TlRneE1Gb1hEVE0wTURFeU9URXhNRE14TUZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBSnZjCmlVNSs5cTN5ZTMvV1M0aUFxTVFQK3dSQjBPdHF0dnJIYU9LVko0WFdTc1lBejNWT0xDcGU3bkY4bWxuWExHeDkKWU5xVmZPOGUzZHFQZnJqa0RMc3lrTGJVRGJ5Sy84SWRuR0ZGOERqYm9mODAra2IyL0dFQzV0T3BPcjhpdDFUMApBZ3RGbzNMdHNUMjNTaGhycHFRU1dPVnoxdFVlZjQyWTYwR01hbE4xWG5jRDgxZHhadG5hbXh5UXIwdzI4Rm1MClUvcExxblBtWlk2b21vS0h1eTJ6MVJzZmZXOUJvY2JrKzRPSXVQSGNLTEgwcTJRYyt0Nlkza3BZWllYeFZEYTEKWFZkdjZtTU5LamUvWkc4bEFtazB2bXJYcldzeW9wdWlhdzhINnJBRjVONndjS0ZoNWJ0UUh0TEJTOXZzUUF0QwppOXNtSHpWNHpCNGNpdkdtU3FzQ0F3RUFBYU5GTUVNd0RnWURWUjBQQVFIL0JBUURBZ0trTUJJR0ExVWRFd0VCCi93UUlNQVlCQWY4Q0FRQXdIUVlEVlIwT0JCWUVGTTZHRlN6R1NOQWRLbmpNc0xBNGtsQVJtaFcvTUEwR0NTcUcKU0liM0RRRUJDd1VBQTRJQkFRQndpTkRueXFJOHk3b3FYaWZRZmxXQlYvQ1NiSlJueVpYUW1mNDM1bUx5WWI0TQpiSytPL3RnWWVEWDUrSmRsQ3RHNGpDTWhqQnFCNTFuWUxseU5lc1RJMXZIcUV0UGhtdTlhNWp2bVc3VjBzbldnCmVmWnR4OFlFc2lxTUttdmUvalRtM2ViZ2d1S1JWZEFRNEpGanFucUNxaStXSmFDR2FjOXFxcExaUlN1eXJGWGgKZkhZUC9Tc0ZiM1dmNFFUUGVLSWQyWXhzRXZ5VU9MK1Rra1ZCckZnOWo5eE5MRHhDak44ZFVia1cxdlQwbHFOcgpjbkpRZXhEZjB3QlVHdEVvb1ByZXU5WG5Ma0R1NHduWFFhM0kzdkFZWHNLUm1iODRpTHdZZlVyWUFycUo2UDBKCjd0Y3JtNU5DWUJISEtaRFo5cTc3SzIvUFl6TjhFeGZqM2Mxei8yS0YKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="

export INPUT_DB_EP1="az-b.database-hyun.fe214376ac7e402590083b76d98ff5f5.mysql.managed-service.kr-central-2.kakaocloud.com"
export INPUT_DB_EP2="az-a.database-hyun.fe214376ac7e402590083b76d98ff5f5.mysql.managed-service.kr-central-2.kakaocloud.com"

DB_EP1=$(echo -n "$INPUT_DB_EP1" | base64 -w 0)
DB_EP2=$(echo -n "$INPUT_DB_EP2" | base64 -w 0)

sudo tee -a /etc/environment << EOF
export JAVA_VERSION="17"
export SPRING_BOOT_VERSION="3.1.0"
export DOCKER_IMAGE_NAME="demo-spring-boot"
export DOCKER_JAVA_VERSION="17-jdk-slim"
EOF

source /etc/environment

sudo mkdir /home/ubuntu/yaml
sudo chmod 777 /home/ubuntu/yaml
sudo wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/lab6Yaml.tar -O /home/ubuntu/yaml/lab6Yaml.tar

sudo cat <<EOF > /home/ubuntu/yaml/lab6-Secret.yaml
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

sudo cat <<EOF > /home/ubuntu/yaml/lab6-Deployment.yaml
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
        image: ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/demo-spring-boot:1.0
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

sudo cat <<EOF > /home/ubuntu/yaml/lab6-ConfigMapDB.yaml
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

sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

sudo mkdir /home/ubuntu/.kube

sudo cat <<EOF > /home/ubuntu/.kube/config
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

 sudo wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O /usr/local/bin/kic-iam-auth
sudo chmod +x /usr/local/bin/kic-iam-auth


sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
sudo echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo chmod 666 /var/run/docker.sock

sudo apt install unzip
sudo apt-get install -y openjdk-17-jdk maven

sudo chmod 600 /home/ubuntu/.kube/config
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config

sudo cat <<EOF > /home/ubuntu/values.yaml

replicaCount: 2

deployment:
  repository: ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/demo-spring-boot
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
