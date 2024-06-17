# Kubeflow 하이퍼파라미터 튜닝
하이퍼파라미터 튜닝을 위해 트레이닝 이미지를 직접 빌드하고 컨테이너 레지스트리에 이미지를 푸시합니다. 이 과정을 통해 Experiment를 생성하여 최적의 하이퍼파라미터를 찾는 방법을 자동화하는 실습을 진행합니다.

## 1. Container Registry 생성
**Note** : 카카오 클라우드 자동 로그아웃 된 경우, 조직이름 : kakaocloud-edu 입력 후 진행
1. 카카오 클라우드 콘솔 > Container Pack > Container Registry > Repository
2. Repository 탭 > `+ 리포지토리 만들기` 클릭
   - 리포지토리 설정 정보
      - 공개 여부 : `비공개`
      - 리포지토리 이름 : `kakao-registry`
      - 태그 덮어쓰기 : `가능`
      - 이미지 스캔 : `자동`
   - `만들기` 클릭
3. 생성된 `kakao-registry` 클릭
4. 생성된 Container Registry 확인

## 2. Bastion VM 생성 및 준비
1. VM 생성 전 스크립트 작성
   - **Note**:아래 스크립트를 메모장에 붙여넣기
   - **Note**:메모장에 붙여넣기 시 작은따옴표('') 안에 입력
   #### **lab6-2-1**
   ```bash
   #!/bin/bash
   
   echo "kakaocloud: 1. 환경 변수 설정 시작"
   # 환경 변수 설정
   command=$(cat <<EOF
   export ACC_KEY='액세스 키 아이디 입력'
   export SEC_KEY='보안 액세스 키 입력'
   export EMAIL_ADDRESS='사용자 이메일 입력'
   export AUTH_DATA='클러스터의 certificate-authority-data 값 입력'
   export API_SERVER='클러스터의 server 값 입력'
   export CLUSTER_NAME='클러스터 이름 입력'
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
   wget -O /home/ubuntu/mnist_train.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/mnist_train.py
   wget -O /home/ubuntu/Experiment.template.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Experiment.template.yaml

   # Experiment.yaml 파일 생성
   envsubst < /home/ubuntu/Experiment.template.yaml > /home/ubuntu/Experiment.yaml
   rm /home/ubuntu/Experiment.template.yaml
   echo "kakaocloud: 하이퍼파라미터 파일 다운로드 완료"
   
   echo "kakaocloud: 모든 설정이 완료되었습니다."
   ```

2. Lab1-4에서 복사해둔 사용자 액세스 키 ID와 사용자 액세스 보안 키를 스크립트 메모장에 붙여넣기
3. 카카오 클라우드 콘솔 > Container Pack > Kubernetes > Cluster
4. 프로젝트 이름 메모장에 붙여넣은 후 `kubectl` 버튼 클릭
5. kubeconfilg 파일 다운로드 후 파일 열기
   - 왼쪽 상단에 있는 프로젝트 이름 복사 후 메모장에 붙여넣기
   - `kubectl` 버튼 클릭
   - `kubeconfilg 파일 다운로드` 버튼 클릭 후 파일 열기
      - **Note**: 연결 프로그램을 메모장으로 열기 (다른 SDK 환경도 가능)
6. clusters 하위의 `certificate-authority-data`, `server`, `name` 값 메모장에 붙여넣기
        ![image](https://github.com/KOlizer/tutorial/assets/127844467/362b8588-156a-4fc7-9f9b-add2574162d5)
7. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine > Instance
8. `Instance 만들기` 클릭
   - 인스턴스 설정 정보
      - 기본 정보
         - 이름 : `bastion`
         - 개수 : `1`
      - 이미지 : `Ubuntu 22.04 - 5.15.0-100 (NVIDIA 550.54.14)`
      - 인스턴스 유형 : `t1i.xlarge`
      - 볼륨
         - 루트 볼륨 : `30 GB`
      - 키 페어 : `생성해둔 keypair` 선택
      - 네트워크
         - VPC : `vpc_k8s` 선택
         - 서브넷 : `main` 선택
         - 보안 그룹
            - `보안 그룹 생성` 클릭 
            - 보안그룹 설정 정보
               - 보안 그룹 이름 : `bastion`
               - 보안 그룹 설명(선택) : 빈칸
               - 인바운드 정보
                  - 1번째 인바운드
                     - 프로토콜 : `TCP`
                     - 패킷 출발지 : `교육장의 사설 IP/32`
                     - 포트번호 : `22`
                     - 추가하기 클릭
                  - 2번째 인바운드
                     - 프로토콜 : `TCP`
                     - 패킷 출발지 : `0.0.0.0/0`
                     - 포트번호 : `8080`
                  - 아웃바운드 탭 클릭
               - 아웃바운드 정보
                  - 프로토콜 : `ALL`
                  - 패킷 출발지 : `0.0.0.0/0`
                  - 포트번호 : `ALL`
               - `생성` 클릭
            - `bastion` 선택
      - 하단의 고급설정 클릭
      - 사용자 스크립트에 Lab6-4까지 작성한 메모장 내용 붙여넣기
         - **Note**: 가상머신을 생성할 때 고급 설정 스크립트 부분을 설정하지 못하였더라도 추후 설정할 수 있습니다.
   - `생성` 클릭
9. 인스턴스에 퍼블릭 IP 연결
   - 생성된 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
   - `새로운 Public IP를 생성하고 자동으로 할당` 선택
   - `확인` 버튼 클릭
10. 인스턴스에 SSH 연결
   - 생성된 인스턴스의 우측 메뉴바 > SSH 연결 클릭
   - SSH 접속 명령어 복사
   - 터미널 열기
   - keypair를 다운받아놓은 폴더로 이동
     #### **lab6-2-9-1**
     ```bash
     cd {keypair.pem 다운로드 위치(보통 자신의 홈 디렉터리 하위의 Downloads 경로에 존재)}
     ```
   - 터미널에 명령어 붙여넣기
     #### **lab6-2-9-2**
     ```bash
     ssh -i keypair.pem ubuntu@{bastion의 public ip주소}
     ```
   - yes 입력
     #### **6-2-9-3**
     ```bash
     yes
     ```
     
   - **Note**: 윈도우에서 ssh 접근이 안될 경우에 cmd 창에서 keypair.pem가 있는 경로로 이동 후 아래 명령어 입력
     #### **6-2-9-4**
     ```bash
     icacls.exe keypair.pem /reset
     icacls.exe keypair.pem /grant:r %username%:(R)
     icacls.exe keypair.pem /inheritance:r
     ```

### Note : 10번은 고급설정을 진행하지 않았을 때만 진행합니다
11. **bastion 생성 시에 고급 설정을 진행하지 않았을 때 진행**
   - 메모장에 작성해 놓은 스크립트 전체 복사
12. 복사한 스크립트 명령어 bastion 터미널에 붙여 넣기
13. cloud-init log 확인하는 명령어 입력
   - **Note**: 터미널 창이 작으면 로그가 안보일 수도 있으니, 터미널 창의 크기를 늘려주세요.
   #### **6-2-11**
   ```bash
   watch -c 'awk "/kakaocloud:/ {gsub(/([0-9]+)\\./, \"\\033[33m&\\033[0m\"); print}" < /var/log/cloud-init-output.log'
   ```
   - **Note**: 설치 확인 화면 `ctrl+c`로 빠져나오기

14. 하이퍼파라미터 파일 다운로드 확인
   #### **6-2-12**
   ```bash
   ls
   ```
15. kubectl get nodes를 통해 생성했던 노드들 조회(총 8개)
   #### **6-2-13**
   ```bash
   kubectl get nodes
   ```
16. Dockerfile 내용 조회
   #### **6-2-14**
   ```bash
    cat Dockerfile
   ```
17. mnist_train.py 내용 조회
   #### **6-2-15**
   ```bash
   cat mnist_train.py 
   ```

## 3. 도커 이미지 생성 및 레지스트리 등록
1. 이미지 빌드
   #### **lab6-3-1**
   ```bash
   docker build -t hyperpram:1.0 .
   ```
2. 빌드된 이미지 확인
   #### **lab6-3-2**
   ```bash
   docker images
   ```
3. 테스트로 이미지 실행
   #### **lab6-3-3**
   ```bash
   docker run -d hyperpram:1.0
   ```
4. 도커 로그인
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   #### **lab6-3-4**
   ```bash
   docker login ${PROJECT_NAME}.kr-central-2.kcr.dev --username ${ACC_KEY} --password ${SEC_KEY}
   ```
5. 이미지 Push를 위한 태깅
   #### **lab6-3-5**
   ```bash
   docker tag hyperpram:1.0 ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/hyperpram:1.0
   ```
6. 이미지가 정상적으로 태그 되었는지 확인
   #### **lab6-3-6**
   ```bash
   docker images
   ```
7. 이미지 업로드
   #### **lab6-3-7**
   ```bash
   docker push ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/hyperpram:1.0
   ```
8. 카카오 클라우드 콘솔 > Container Pack > Container Resistry > Repository
9. `kakao-registry` 클릭
10. hyperpram 이미지 생성 확인

   ![image](https://github.com/KOlizer/tutorial/assets/127844467/8473733e-5591-4dd8-af27-70d3bbe30c69)

11. bastion VM 터미널에서 시크릿 키 생성
   #### **lab6-3-11**
   ```bash
   kubectl create secret docker-registry regcred \
   --docker-server=kakao-sw-club.kr-central-2.kcr.dev \
   --docker-username=${ACC_KEY} \
   --docker-password=${SEC_KEY} \
   --docker-email=${EMAIL_ADDRESS}
   ```
12. 시크릿 키 생성 확인
   #### **lab6-3-13**
   ```bash
   kubectl get secret -n kbm-u-kubeflow-tutorial
   ```

## 4. Kubeflow UI에서 Experiment 생성
1. 깃허브 lab6-4-1 Experiment 설정 파일을 메모장에 붙여넣기
      - **Note**:아래 스크립트를 메모장에 붙여넣기
    #### **lab6-4-1**
    ```bash
   apiVersion: "kubeflow.org/v1beta1"
   kind: Experiment
   metadata:
     name: mnist-hyperparameter-tuning
     namespace: kubeflow
   spec:
     objective:
       type: maximize
       goal: 0.99
       objectiveMetricName: accuracy
       additionalMetricNames:
         - loss
     algorithm:
       algorithmName: random
     parallelTrialCount: 10
     maxTrialCount: 12
     maxFailedTrialCount: 3
     parameters:
       - name: --learning_rate
         parameterType: double
         feasibleSpace:
           min: "0.0001"
           max: "0.01"
       - name: --batch_size
         parameterType: int
         feasibleSpace:
           min: "16"
           max: "128"
     trialTemplate:
       retain: true
       primaryContainerName: mnist-training
       trialParameters:
         - name: learningRate
           description: Learning rate for the model
           reference: --learning_rate
         - name: batchSize
           description: Batch size for the model
           reference: --batch_size
       trialSpec:
         apiVersion: batch/v1
         kind: Job
         spec:
           template:
             metadata:
               annotations:
                 sidecar.istio.io/inject: 'false'
             spec:
               containers:
                 - name: mnist-training
                   image: ${프로젝트 이름}.kr-central-2.kcr.dev/kakao-registry/hyperpram:1.0
                   command:
                     - "python"
                     - "mnist_train.py"
                     - "--learning_rate=${trialParameters.learningRate}"
                     - "--batch_size=${trialParameters.batchSize}"
               restartPolicy: Never
               imagePullSecrets:
                 - name: regcred
     metricsCollectorSpec:
       source:
         filter:
           metricsFormat:
             - "{metricName: ([\\w|-]+), metricValue: ((-?\\d+)(\\.\\d+)?)}"
         fileSystemPath:
           path: "/tmp/mnist.log"
           kind: File
       collector:
         kind: File
    ```

2. 카카오클라우드 콘솔 왼쪽 상단에 있는 프로젝트 이름 복사 후 메모장에 붙여넣기
3. Kubeflow 대시보드의 Experiments (AutoML) 탭 > `New Experiment` 버튼 클릭
4. 하단의 `Edit` 클릭
5. 기존 내용을 지운 뒤 Experiment 설정 파일 내용 삽입
   - 기존 내용 지우기
   - Experiment 설정 파일 내용 삽입
   - `CREATE` 버튼 클릭

## 5. Experiment 결과 확인
1. 생성된 mnist-hyperparameter-tuning 클릭
2. OVERVIEW 탭 확인
   - OVERVIEW 탭 클릭
3. TRIALS 탭 확인
   - TRIALS 탭 클릭
4. DETAILS 탭 확인
   - DETAILS 탭 클릭

## 6. K8s의 내부 동작 살펴보기
   - **Note**: bastion VM 접속 터미널 창에 아래 명령어들을 입력하세요.
1. Experiment 생성함
   #### **lab6-6-1**
   ```
   kubectl get Experiment -n kbm-u-kubeflow-tutorial
   ```
2. Experiment Controller가 Suggestion을 생성함
   #### **lab6-6-2**
   ```
   kubectl get Suggestion -n kbm-u-kubeflow-tutorial
   ```
3. Trial Controller가 Suggestion에 작성된 하이퍼파라미터 설정을 기반으로 Trial들을 생성 > Trial들이 Job을 생성 > Job이 Pod들을 생성함
   #### **lab6-6-3-1**
   - 현재 네임스페이스에서 실행 중인 Trial 목록 확인
   - **Note**: Trial - 제안된 하이퍼파라미터 설정에 따라 생성된 실험 실행 단위
   ```
   kubectl get trials -n kbm-u-kubeflow-tutorial
   ```
   
   #### **lab6-6-3-2**
   - 현재 네임스페이스에서 실행 중인 Job 목록 확인
   - **Note**: Job - 각 Trial에서 수행되는 작업으로, 실제 모델 학습 등의 작업 처리
   ```
   kubectl get job -n kbm-u-kubeflow-tutorial
   ```

   #### **lab6-6-3-3**
   - 현재 네임스페이스에서 실행 중인 Pod 목록 확인
   - **Note**: Pod - Job에 의해 생성된 컨테이너 단위로, 실제 컴퓨팅 리소스를 사용하여 작업 수행
   ```
   kubectl get po -n kbm-u-kubeflow-tutorial
   ```
