## Kubeflow 하이퍼파라미터 튜닝
하이퍼파라미터 튜닝을 위해 트레이닝 이미지를 직접 빌드하고 컨테이너 레지스트리에 이미지를 푸시합니다. 이 과정을 통해 Experiment를 생성하여 최적의 하이퍼파라미터를 찾는 방법을 자동화하는 실습을 진행합니다.

### 1. Container Registry 생성
1. 카카오 클라우드 콘솔 > Container Pack > Container Registry
2. Repository 탭 > `+리포지토리 만들기` 클릭
   - 리포지토리 설정
     - 공개 여부 : `비공개` 선택
     - 리포지토리 이름 : `kakao-registry`
     - 태그 덮어쓰기 : `가능` 선택
3. `만들기` 클릭
4. 생성된 `kakao-registry` 클릭

### 2. Bastion VM 생성 및 준비
1. VM 생성 전 스크립트 작성
   1. 아래 스크립트를 메모장에 붙여넣기
   #### **lab6-2-1-1**
   ```bash
   #!/bin/bash

    echo "kakaocloud: 1. 환경 변수 설정 시작"
    # 환경 변수 설정
    command=$(cat <<EOF
    export ACC_KEY='액세스 키 아이디 입력'
    export SEC_KEY='보안 액세스 키 입력'
    export EMAIL_ADDRESS='사용자 이메일 입력'
    export CLUSTER_NAME='클러스터 이름 입력'
    export AUTH_DATA='클러스터의 certificate-authority-data 값 입력'
    export API_SERVER='클러스터의 server 값 입력'
    export PROJECT_NAME='프로젝트 이름 입력'
    EOF
    )
    
    # 환경 변수를 평가하고 .bashrc에 추가
    eval "$command"
    echo "$command" >> /home/ubuntu/.bashrc
    source /home/ubuntu/.bashrc
    echo "kakaocloud: 환경 변수 설정 완료"
    
    echo "kakaocloud: 2. 도커 설치 시작"
    # 도커 설치
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 
    sudo apt update
    apt-get install -y docker-ce docker-ce-cli containerd.io 
    chmod 666 /var/run/docker.sock 
    echo "kakaocloud: 도커 설치 완료"
    
    echo "kakaocloud: 3. kubectl 설치 시작"
    # kubectl 설치
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    echo "kakaocloud: kubectl 설치 완료"
    
    echo "kakaocloud: 4. kic-iam-auth 설치 시작"
    # kic-iam-auth 설치
    wget -O /usr/local/bin/kic-iam-auth https://objectstorage.kr-central-2.kakaoi.io/v1/fe631cd1b7a14c0ba2612d031a8a5619/public/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth
    chmod +x /usr/local/bin/kic-iam-auth
    echo "kakaocloud: kic-iam-auth 설치 완료"
    
    echo "kakaocloud: 5. kube config 설정 시작"
    # kube config 설정
    mkdir -p /home/ubuntu/.kube
    if [ -f /home/ubuntu/.kube/config ]; then
        rm /home/ubuntu/.kube/config
    fi
    wget -O /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/kube-config.yaml
    envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config
    chmod 600 /home/ubuntu/.kube/config
    chown ubuntu:ubuntu /home/ubuntu/.kube/config
    echo "kakaocloud: kube config 설정 완료"
    
    echo "kakaocloud: 6. 하이퍼파라미터 파일 다운로드 시작"
    # 기존 파일 삭제
    if [ -f /home/ubuntu/Dockerfile ]; then
        rm /home/ubuntu/Dockerfile
    fi
    if [ -f /home/ubuntu/Experiment.yaml ]; then
        rm /home/ubuntu/Experiment.yaml
    fi
    if [ -f /home/ubuntu/mnist_train.py ]; then
        rm /home/ubuntu/mnist_train.py
    fi
    
    # 하이퍼파라미터에 필요한 파일 다운로드
    wget -O /home/ubuntu/Dockerfile https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Dockerfile 
    wget -O /home/ubuntu/Experiment.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Experiment.yaml 
    wget -O /home/ubuntu/mnist_train.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/mnist_train.py 
    echo "kakaocloud: 하이퍼파라미터 파일 다운로드 완료"
    
    echo "kakaocloud: 모든 설정이 완료되었습니다."
   ```
   2. Lab1-4 에서 복사해둔 사용자 액세스 키 ID와 사용자 액세스 보안 키를 스크립트 메모장에 붙여넣기
   3. 카카오 클라우드 콘솔 > 서비스 > Container Pack > Kubernetes > Cluster
      - 프로젝트 이름 메모장에 붙여넣기
   4. `kubectl` 버튼 클릭
   5. kubeconfilg 파일 다운로드 후 파일 열기
      - **Note**: 연결 프로그램을 메모장으로 열기 (다른 SDK 환경도 가능)
      - clusters 하위의 `certificate-authority-data`, `name` 값 메모장에 붙여넣기
        ![image](https://github.com/KOlizer/tutorial/assets/127844467/362b8588-156a-4fc7-9f9b-add2574162d5)
2. Instance 만들기
   1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > Instance
   2. `Instance 만들기` 클릭
      - 인스턴스 설정 정보
        - 이름 : bastion
        - 개수 : 1
        - Image : Ubuntu 22.04 - 5.15.0-100 (NVIDIA 550.54.14)
        - Instance 타입 : t1i.xlarge
        - Volume : 30 GB
        - 키페어 : 생성해둔 keypair 선택
        - vpc : vpc_k8s 선택
        - 서브넷 : main 선택
        - 보안그룹 : 선택된 항목 선택
          - 보안그룹 설정 정보
            - 보안 그룹 이름 : bastion
            - 인바운드 정보
              - 1 번째 인바운드
                - 프로토콜 : TCP
                - 패킷 출발지 : 교육장의 사설 IP/32
                - 포트번호 : 22
              - 2 번째 인바운드
                - 프로토콜 : TCP
                - 패킷 출발지 : 0.0.0.0/0
                - 포트번호 : 8080
            - 아웃바운드 정보
              - 프로토콜 : ALL
              - 패킷 출발지 : 0.0.0.0/0
              - 포트번호 : ALL
          - `생성` 클릭
        - 보안그룹 : bastion 선택
        - 하단의 고급설정 클릭
          - 사용자 스크립트에 Lab6-2 메모장 내용 붙여넣기
             **Note**: 가상머신을 생성할 때 고급 설정 스크립트 부분을 설정하지 못하였더라도 추후 설정할 수 있습니다.
   3. `생성` 클릭
3. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
4. 생성된 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
   - `새로운 Public IP를 생성하고 자동으로 할당` 선택
5. `확인` 버튼 클릭
6. 생성된 인스턴스의 우측 메뉴바 > SSH 연결 클릭
   - SSH 접속 명령어 복사 (다운받은 keypair.pem 파일이 있는 경로에서 아래 명령어를 실행합니다.)
   - 터미널 열기
   - keypair를 다운받아놓은 폴더로 이동
     #### **lab6-2-6-1**
     ```bash
     cd {keypair.pem 다운로드 위치}
     ```
   - 터미널에 명령어 붙여넣기
     #### **lab6-2-6-2**
     ```bash
     ssh -i keypair.pem ubuntu@{bastion의 public ip주소}
     ```
   - yes 입력
     #### **lab6-2-6-3**
     ```bash
     yes
     ```
   - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
     #### **lab6-2-6-4**
     ```bash
     icacls.exe keypair.pem /reset
     icacls.exe keypair.pem /grant:r %username%:(R)
     icacls.exe keypair.pem /inheritance:r
     ```

#### Note : 7,8번은 고급설정을 진행하지 않았을 때만 진행합니다

7. 메모장에 작성해 놓은 스크립트 전체 복사
8. 복사한 스크립트 명령어 bastion 터미널에 붙여 넣기
9. cloud-init log 확인하는 명령어 입력 사용자가 스크립트를 통해 미리 준비해둔 하이퍼파라미터 실습 파일 조회
   - 사용자 스크립트를 통해 미리 준비해둔 하이퍼파라미터 실습 파일 조회
   - **Note**: 터미널 창이 작으면 로그가 안보일 수도 있으니, 터미널 창의 크기를 늘려주세요.
   #### **lab6-2-9-1**
   ```bash
   watch -c 'awk "/kakaocloud:/ {gsub(/([0-9]+)\\./, \"\\033[33m&\\033[0m\"); print}" < /var/log/cloud-init-output.log'
   ```

### 3. Kubeflow 하이퍼파라미터 튜닝
1. 하이퍼파라미터 파일 다운로드 확인
   **Note**: 아래의 명령어를 순서대로 복사하여 터미널에 붙여넣기
   #### **lab6-3-1**
   ```bash
   ls -l /home/ubuntu/Dockerfile
   ls -l /home/ubuntu/Experiment.yaml
   ls -l /home/ubuntu/mnist_train.py
   ```
2. `kubectl get nodes`를 통해 생성했던 노드들 조회
   #### **lab6-3-2**
   ```bash
   kubectl get nodes
   ```
3. Dockerfile 내용 조회
   #### **lab6-3-3**
   ```bash
   cat Dockerfile
   ```
4. mnist_train.py 내용 조회
   #### **lab6-3-4**
   ```bash
   cat mnist_train.py 
   ```
5. Experiment.yaml 내용 조회
   #### **lab6-3-5**
   ```bash
   cat Experiment.yaml
   ```

### 4. 도커 이미지 생성 및 레지스트리 등록
1. 이미지 빌드하기
   #### **lab6-4-1**
   ```bash
   docker build -t hyperpram:1.0 .
   ```
2. 빌드된 이미지 확인
   #### **lab6-4-2**
   ```bash
   docker images
   ```
3. 테스트로 이미지 실행 (run) 해보기 
   #### **lab6-4-3**
   ```bash
   docker run -d hyperpram:1.0
   ```
4. 도커 로그인
   - **Note**: Lab1-4 에서 복사해둔 사용자 액세스 키 ID와 사용자 액세스 보안 키 붙여넣기
   #### **lab6-4-4**
   ```bash
   docker login {프로젝트 이름}.kr-central-2.kcr.dev --username {사용자 액세스 키 ID} --password {사용자 액세스 보안 키}
   ```
5. 카카오 클라우드 콘솔 > 서비스 > Container Pack > Container Resistry > Repository
6. `kakao-registry` 클릭
7. hyperpram 이미지 생성 확인

   ![image](https://github.com/KOlizer/tutorial/assets/127844467/8473733e-5591-4dd8-af27-70d3bbe30c69)

8. 깃허브 lab6-8-1스크립트를 메모장에 붙여넣기
   #### **lab6-8-1**
   ```bash
   kubectl create secret docker-registry regcred \
   --docker-server=kakao-sw-club.kr-central-2.kcr.dev \
   --docker-username={액세스 키 아이디} \
   --docker-password={보안 액세스 키} \
   --docker-email={사용자 이메일} \
   --namespace={사용자 네임스페이스}
   ```
   - Lab1-4 에서 복사해둔 사용자 액세스 키 ID와 사용자 액세스 보안 키 메모장에 붙여넣기
   - Kubeflow 대시보드 > 네임스페이스 복사
   
     ![image](https://github.com/KOlizer/tutorial/assets/127844467/bdbcca75-604b-45e9-a455-c74af1edcaab)
     
   - {사용자 이메일}에 사용자의 이메일 입력 
9. bastion VM 터미널에 작성된 명령어를 입력하여 시크릿 키 생성
