# K8s engine Cluster 관리 VM 생성 실습

클러스터를 관리하기 위한 Bation VM 인스턴스를 생성하는 실습입니다.

## 1. Bastion VM 인스턴스 생성

1. 카카오 클라우드 콘솔 > Container Pack > Kubernetes > Cluster 접속
2. 클러스터 `kakao-k8s-cluster` 클릭
  - 서버 엔드 포인트 복사 후 메모장에 붙여넣기
3. kubectl 버튼 클릭
  - kubeconfig 파일 다운로드 클릭
    - kubeconfig 파일 열기
    - certificate-authority-data(인증 데이터), name(클러스터 이름) 값 복사 후 메모장에 붙여넣기
4. 카카오 클라우드 콘솔 > Data Store > MySQL 접속
5. 생성된 MySQL 인스턴스 그룹 클릭
  - az-a의 엔드포인트 주소와 az-b의 엔드포인트 주소를 순서대로 복사 후 메모장에 붙여넣기
  - 왼쪽 상단에 있는 프로젝트 이름 복사 후 메모장에 붙여넣기


6. 사용자 스크립트 작성
   - 스크립트를 메모장에 복사후 복사해놓은 값들을 입력하기
     - 사용자 엑세스 키 ID, 사용자 엑세스 보안 키
     - 클러스터 API 엔드포인트
     - 클러스터 이름
     - certificate-authority-data(인증 데이터)
     - 프로젝트 이름, database az-a의 엔드포인트, database az-b의 엔드포인트
     - 이메일(사용자 지정 입력)
     - 이미지 이름(사용자 지정 입력)
     - 자바 버전(사용자 지정 입력)
      
      ### **Note**:
     서버와 데이터베이스 통신시, 순서대로 진행하므로 꼭 database az-a의 엔드포인트, database az-b의 엔드포인트 순서대로 붙여넣어주세요. 
   #### **lab3-1-6**
     - **Note**: 사용자는 export ACC_KEY부터 DOCKER_JAVA_VERSION까지만 입력해주세요.
     - **Note**: 작은따옴표를 없애지 말고 사용자 입력값을 넣어주세요.
     - **Note**: 맥 OS 사용자의 경우 사용자 입력 시에 작은따옴표가 자동 변환되는 경우가 빈번하니, https://n.lrl.kr/ 같은 메모장 사이트를 이용해 주세요.
   ```bash
   #!/bin/bash

   echo "kakaocloud: 1.Starting environment variable setup"
   # 환경 변수 설정: 사용자는 이 부분에 자신의 환경에 맞는 값을 입력해야 합니다.
   command=$(cat <<EOF
   export ACC_KEY='사용자 액세스 키 ID 입력'
   export SEC_KEY='사용자 액세스 보안 키 입력'
   export EMAIL_ADDRESS='사용자 이메일 입력'
   export CLUSTER_NAME='클러스터 이름 입력'
   export API_SERVER='클러스터의 API 엔드포인트 입력'
   export AUTH_DATA='클러스터의 certificate-authority-data 입력'
   export PROJECT_NAME='프로젝트 이름 입력'
   export INPUT_DB_EP1='데이터베이스 1의 엔드포인트 입력'
   export INPUT_DB_EP2='데이터베이스 2의 엔드포인트 입력'
   export DOCKER_IMAGE_NAME='이미지 이름 입력(demo-spring-boot)'
   export DOCKER_JAVA_VERSION='자바 버전 입력(17-jdk-slim)'
   export JAVA_VERSION='17'
   export SPRING_BOOT_VERSION='3.1.0'
   export DB_EP1=\$(echo -n "\$INPUT_DB_EP1" | base64 -w 0)
   export DB_EP2=\$(echo -n "\$INPUT_DB_EP2" | base64 -w 0)
   EOF
   )

   eval "$command"
   echo "$command" >> /home/ubuntu/.bashrc
   echo "kakaocloud: Environment variable setup completed"

   echo "kakaocloud: 2.Checking the validity of the script download site"
   curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/script/script.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
   echo "kakaocloud: Script download site is valid"
  
   wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/script/script.sh
   chmod +x script.sh
   sudo -E ./script.sh
   ```
    
8. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > Instance 접속
9. Instance 만들기 클릭
   - 이름 : `bastion`
   - Image : `Ubuntu 20.04 - 5.4.0-164`
   - Instance 타입 : `t1i.xlarge`
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
      - 패킷 출발지: `{교육장의 사설 IP}/32`
        - **Note**: "교육장의 사설 IP" 부분을 실제 IP 주소로 교체하세요.
      - 포트 번호: `22`
      - 프로토콜: `TCP`
      - 패킷 출발지: `0.0.0.0/0`
      - 포트 번호: `8080`
13. Outbound 클릭
    - Outbound
      - 프로토콜 : `ALL`
      - 패킷 목적지 : `0.0.0.0/0`
    - 만들기 버튼 클릭
14. 고급설정 버튼 클릭
    - 사용자 스크립트에 [**lab3-1-6**](https://github.com/kakaocloud-edu/tutorial/blob/main/AdvancedCourse/PracticalTextbook/Lab03.md#lab3-1-6) 내용을 붙여넣기
      - **Note**: 가상머신을 생성할 때 고급 설정 스크립트 부분을 설정하지 못하였더라도 [추후 설정](https://github.com/kakaocloud-edu/tutorial/blob/main/AdvancedCourse/PracticalTextbook/Lab03.md#note--19%EB%B2%88%EC%9D%80-%EA%B3%A0%EA%B8%89%EC%84%A4%EC%A0%95%EC%9D%84-%EC%A7%84%ED%96%89%ED%95%98%EC%A7%80-%EC%95%8A%EC%95%98%EC%9D%84-%EB%95%8C%EB%A7%8C-%EC%A7%84%ED%96%89%ED%95%A9%EB%8B%88%EB%8B%A4)할 수 있습니다.

15. 만들기 버튼 클릭
16. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
17. 생성된 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
    - `새로운 Public IP를 생성하고 자동으로 할당` 
18. 확인 버튼 클릭
19. 생성된 인스턴스의 우측 메뉴바 > SSH 연결 클릭
     - SSH 접속 명령어 복사(다운받은 keypair.pem 파일이 있는 경로에서 아래 명령어를 실행합니다.)
     - 터미널 열기
     - keypair를 다운받아놓은 폴더로 이동
     - 터미널에 명령어 붙여넣기
     - yes 입력
    #### **lab3-1-18-1**
     ```bash
     cd {keypair.pem 다운로드 위치}
     ```
     - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정

     #### **lab3-1-18-2**
     ```bash
     chmod 400 keypair.pem
     ```

     #### **lab3-1-18-3**
     ```bash
     ssh -i keypair.pem ubuntu@{bastion의 public ip주소}
     ```
     - **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.
   
     #### **lab3-1-18-4**
     ```bash
     yes
     ```
    
    - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
     #### **lab3-1-18-5**
     ```bash
     icacls.exe keypair.pem /reset
     icacls.exe keypair.pem /grant:r %username%:(R)
     icacls.exe keypair.pem /inheritance:r
     ```


### Note : 19번은 고급설정을 진행하지 않았을 때만 진행합니다
19. bastion 생성 시에 고급 설정을 진행하지 않았을 때 진행
    - 메모장에 작성해 놓은 스크립트 중, 환경변수 설정 부분만 복사
    - 복사한 환경 변수 설정 명령어 bastion 터미널에 붙여 널기
     #### **lab3-1-19-1**
    - script.sh 파일 내려받기
     ```bash
     wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/script/script.sh
     ```

     #### **lab3-1-19-2**
    - script.sh 파일 권한 설정
     ```bash
     chmod +x script.sh
     ```

     #### **lab3-1-19-3**
    - script.sh 파일 실행
     ```bash
     sudo -E ./script5.sh
     ```
20. cloud-init log 확인 및 YAML 파일 확인
     #### **lab3-1-20-1**
    - [**lab3-1-6**](https://github.com/kakaocloud-edu/tutorial/blob/main/AdvancedCourse/PracticalTextbook/Lab03.md#lab3-1-6)를 통해 진행한 스크립트의 진행상황을 확인
      - **Note**: 터미널 창이 작으면 로그가 안보일 수도 있으니, 터미널 창의 크기를 늘려주세요.
     ```bash
     watch -c 'awk "/kakaocloud:/ {gsub(/([0-9]+)\\./,\"\\033[33m&\\033[0m\"); print}" < /var/log/cloud-init-output.log'
     ```
    - 모든 스크립트가 완료되면 아래와 같음
     ```
      kakaocloud: 1.Starting environment variable setup
      kakaocloud: Environment variable setup completed
      kakaocloud: 2.Checking the validity of the script download site
      kakaocloud: script download site is valid
      kakaocloud: 3.Variables validity test start
      kakaocloud: Variables are valid
      kakaocloud: 4.Github Connection test start
      kakaocloud: Github Connection succeeded
      kakaocloud: 5.Preparing directories and files
      kakaocloud: Directories prepared
      kakaocloud: 6.Downloading YAML files
      kakaocloud: All YAML files downloaded
      kakaocloud: 7.Installing kubectl
      kakaocloud: Kubectl installed
      kakaocloud: 8.Setting up .kube directory and configuration file
      kakaocloud: .kube setup completed
      kakaocloud: 9.Installing kic-iam-auth
      kakaocloud: kic-iam-auth installation completed
      kakaocloud: 10.Installing Docker and setting it up
      kakaocloud: Docker installation and setup completed
      kakaocloud: 11.Installing additional software
      kakaocloud: Additional software installation completed
      kakaocloud: 12.Setting permissions for .kube/config
      kakaocloud: Permissions set for .kube/config
      kakaocloud: 13.Downloading helm-values.yaml and applying environment substitutions
      kakaocloud: Environment substitutions applied and setup completed
     ```

     #### **lab3-1-20-2**
    - config 파일 확인
     ```bash
     cat /home/ubuntu/.kube/config
     ```

     #### **lab3-1-20-3**
    - values.yaml 파일 확인
     ```bash
     cat /home/ubuntu/values.yaml
     ```

     #### **lab3-1-20-4**
    - 다른 YAML 파일들이 있는 디렉토리로 이동
     ```bash
     cd yaml
     ```
     ```bash
     ls -al
     ```

     #### **lab3-1-20-5**
    - lab6-ConfigMapDB.yaml 파일 확인
     ```bash
     cat lab6-ConfigMapDB.yaml
     ```

     #### **lab3-1-20-6**
    - lab6-Deployment.yaml 파일 확인
     ```bash
     cat lab6-Deployment.yaml
     ```

     #### **lab3-1-20-7**
    - lab6-Secret.yaml 파일 확인
     ```bash
     cat lab6-Secret.yaml
     ```
     

     
## 2. Bastion VM 인스턴스를 통해 클러스터 확인


1. 클러스터 확인 명령어
    #### **lab3-2-1**
     ```bash
     kubectl get nodes
     ```
2. 두 개의 노드가 정상적으로 나오는지 확인
