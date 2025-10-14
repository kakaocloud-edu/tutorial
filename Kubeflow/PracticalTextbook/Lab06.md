# Kubeflow 하이퍼파라미터 튜닝

하이퍼파라미터 튜닝을 위해 트레이닝 이미지를 직접 빌드하고 컨테이너 레지스트리에 이미지를 푸시합니다. 이 과정을 통해 Katib Experiment를 생성하여 최적의 하이퍼파라미터를 찾는 방법을 자동화하는 실습을 진행합니다.

## 1. Kakaocloud 콘솔에서 Container Registry 생성
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

## 2. Jupyter Notebook에 접속하여 하이퍼파라미터 튜닝 이미지 빌드 (약 10분 소요)

1. [Kubeflow 대시보드에 접속하기](./Lab02.md#2-kubeflow-대시보드에-접속하기)를 참고하여 Kubeflow 대시보드 접근 및 로그인
2. kbm-u-kubeflow-tutorial 네임스페이스 선택 > 좌측 메뉴바의 `Notebooks` 탭 클릭

    > 기 생성된 Notebook이 없다면 [2. CPU 기반 Notebook 생성 (약 3분 소요)](./Lab04.md#2-cpu-기반-notebook-생성-약-3분-소요)를 참고하여 cpu 또는 gpu 기반 노트북 생성

3. Notebooks 탭 > 접속하는 노트북의 `CONNECT` 클릭
4. 노트북창에서 좌상단 `+` 버튼 클릭하여 New Launcher 페이지 접근
5. Other 중 `Terminal` 클릭

### 2.1. Container Registry 접근을 위한 환경 변수 설정

#### **lab6-2-1**
   ```bash
   export ACC_KEY='액세스 키 아이디 입력'
   export SEC_KEY='보안 액세스 키 입력'
   export EMAIL_ADDRESS='사용자 이메일 입력'
   export AUTH_DATA='클러스터의 certificate-authority-data 값 입력'
   export API_SERVER='클러스터의 server 값 입력'
   export CLUSTER_NAME='클러스터 이름 입력'
   export PROJECT_NAME='프로젝트 이름 입력'
   ```

1. 위 **lab6-2-1** 환경변수를 메모장에 붙여넣기
2. [Lab1-4 액세스 키 준비](./Lab01.md#4-액세스-키-준비-약-1분-소요)에서 복사해둔 사용자 액세스 키 ID와 사용자 액세스 보안 키를 각각 `ACC_KEY` 과 `SEC_KEY` 환경변수에 추가
3. `EMAIL_ADDRESS`에 사용자 이메일 입력
4. KE 클러스터 kubeconfig 파일 내 `clusters[0].cluster.certificate-authority-data` 경로의 인증 데이터 값과 `clusters[0].cluster.server` 경로의 클러스터 이름 값을 각각 `AUTH_DATA` 과 `API_SERVER` 환경변수에 추가

    > 준비된 kubeconfig 파일이 없다면 [1. Bastion VM 인스턴스 생성 > 3.kubeconfig 파일 클릭](../../AdvancedCourse/PracticalTextbook/Lab03.md#1-bastion-vm-인스턴스-생성)를 참고하여 다운로드

5. `CLUSTER_NAME`에 클러스터 이름 입력
6. `PROJECT_NAME`에 카카오클라우드 콘솔 왼쪽 상단에 표시된 프로젝트 이름 입력
7. 환경변수 설정 전문을 복사하고 노트북 터미널에서 .bashrc 파일에 붙여넣기 및 실행

   #### **lab6-2-2**

   ```bash
   # 파일을 열어 하단부에 추가 후 저장
   vi ~/.bashrc
   
   # 저장 후 source 명령으로 적용
   source ~/.bashrc
   ```

### 2.2. Container Registry에 하이퍼파라미터 튜닝 이미지 빌드

1. 노트북에서 빌드 소스 코드 다운로드

   #### **lab6-2-3**

   ```bash
   # 이미지 빌드 소스 경로 생성
   mkdir -p hpt/docker
   ```

2. 빌드 소스 코드 다운로드(3개 파일)

   #### **lab6-2-4**

   ```bash
   wget -O hpt/docker/Dockerfile https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Dockerfile 
   ```

   #### **lab6-2-5**

   ```bash
   wget -O hpt/docker/mnist_train.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/mnist_train.py
   ```



3. 빌드 소스 코드 확인
   #### **lab6-2-6**

   ```bash
   # Dockerfile 스크립트 출력
   cat hpt/docker/Dockerfile
   ```

   #### **lab6-2-7**

   ```bash
   # mnist_train.py 스크립트 출력
   cat hpt/docker/mnist_train.py 
   ```



4. 도커 커멘드를 통한 이미지 빌드

   #### **lab6-2-8**

   ```bash
   cd hpt/docker && docker build -t hyperparam:1.0 .
   ```

5. 빌드된 이미지 확인

   #### **lab6-2-9**
   ```bash
   docker images
   ```

6. 노트북에서 빌드 이미지 실행

   #### **lab6-2-10**
   ```bash
   docker run -it --rm hyperparam:1.0
   ```
   
   #### **lab6-2-11**
   ```bash
   docker run -it --rm hyperparam:1.0 python mnist_train.py --learning_rate 0.02 --batch_size 128
   ```

7. 도커 로그인

   #### **lab6-2-12**
   ```bash
   docker login ${PROJECT_NAME}.kr-central-2.kcr.dev --username ${ACC_KEY} --password ${SEC_KEY}
   ```

8. 이미지 Push를 위한 태깅
   #### **lab6-2-13**
   ```bash
   docker tag hyperparam:1.0 ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/hyperparam:1.0
   ```

9. 이미지가 정상적으로 태그 되었는지 확인
   #### **lab6-2-14**
   ```bash
   docker images
   ```

10. 이미지 푸시
   #### **lab6-2-15**
   ```bash
   docker push ${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/hyperparam:1.0
   ```


### 2.3. 카카오 클라우드 콘솔에서 빌드 이미지 확인 (약 5분 소요)

1. 카카오 클라우드 콘솔 > Container Pack > Container Resistry > 리포지토리 이동
2. `kakao-registry` 리포지토리 클릭
3. 리포지토리 상세 페이지 이미지 목록에서 `hyperparam` 이미지 확인
 

## 3. Katib Experiment 생성 (약 20분 소요)

1. Container Resistry 접근을 위한 시크릿 키 생성

   #### **lab6-3-1**

   ```bash
   kubectl create secret docker-registry regcred \
   --docker-server=${PROJECT_NAME}.kr-central-2.kcr.dev \
   --docker-username=${ACC_KEY} \
   --docker-password=${SEC_KEY} \
   --docker-email=${EMAIL_ADDRESS} \
   --namespace=kbm-u-kubeflow-tutorial
   ```

    > 노트북 커널 재시작으로 인해 환경 변수 재선언 과정이 필요할 수 있음
    > 
    > [2.1. Container Registry 접근을 위한 환경 변수 설정 > lab6-2-2](#lab6-2-2) 참고

2. 시크릿 키 생성 확인

   #### **lab6-3-2**

   ```bash
   kubectl get secret -n kbm-u-kubeflow-tutorial
   ```

3. Katib Experiment 생성을 위한 yaml 스크립트 다운로드

   #### **lab6-3-3**

   ```bash
   wget -O hpt/Experiment.template.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Experiment.template.yaml
   ```

4. 다운로드된 yaml 스크립트 수정

   - 파일 브라우저에서 `hpt` 폴더로 이동
   - `Experiment.template.yaml` 파일 선택 후 우클릭 하여 Rename 클릭
   - `Experiment.yaml`으로 파일명 변경
   - `Experiment.yaml`파일 더블 클릭하여 스크립트 수정
      - Line #50의 `${PROJECT_NAME}`에 카카오클라우드 콘솔 왼쪽 상단에 표시된 프로젝트 이름 입력

5. `Experiment.yaml`파일의 내용 전체 복사

6. Kubeflow 대시보드에서 `Katib Experiments` LNB 메뉴 클릭 > `New Experiment` 버튼 클릭

7. 하단의 `Edit` 버튼 클릭

8. 기존 내용을 지운 뒤 Experiment 설정 파일 내용 삽입
   - 기존 내용 지우기
   - Experiment YAML 스크립트 전문 삽입
   - `CREATE` 버튼 클릭

## 4. Experiment 결과 확인

1. Kubeflow 대시보드 Experiment 목록 페이지에서 `mnist-hyperparameter-tuning` 이름 클릭

2. OVERVIEW 탭 확인
   - OVERVIEW 탭 클릭

3. TRIALS 탭 확인
   - TRIALS 탭 클릭

4. DETAILS 탭 확인
   - DETAILS 탭 클릭

## 5. Kubeflow 내부 동작 살펴보기
   - **Note**: 노트북 터미널 창에 아래 명령어들을 입력하세요.
   - Katib Controller가 단계적으로 `Experiment`, `Suggestion`, `Trial`의 Katib CR을 생성함
   
1. Katib `Experiment` 조회

   #### **lab6-6-3-4**

   ```
   kubectl get Experiment -n kbm-u-kubeflow-tutorial
   ```

2. Katib `Suggestion` 조회

   #### **lab6-6-3-5**

   ```
   kubectl get Suggestion -n kbm-u-kubeflow-tutorial
   ```

3. Katib `Suggestion` 이하 `Trial` 조회
   - Suggestion에 작성된 하이퍼파라미터 설정을 기반으로 Trial들을 생성 > Trial들이 Job을 생성 > Job Pod가 생성됨

   #### **lab6-6-3-6**
   - 현재 네임스페이스에서 실행 중인 Trial 목록 확인
   - **Note**: Trial - 제안된 하이퍼파라미터 설정에 따라 생성된 실험 실행 단위
   ```
   kubectl get trials -n kbm-u-kubeflow-tutorial
   ```
   
   #### **lab6-6-3-7**
   - 현재 네임스페이스에서 실행 중인 Job 목록 확인
   - **Note**: Job - 각 Trial에서 수행되는 작업으로, 실제 모델 학습 등의 작업 처리
   ```
   kubectl get job -n kbm-u-kubeflow-tutorial
   ```

   #### **lab6-6-3-8**
   - 현재 네임스페이스에서 실행 중인 Pod 목록 확인
   - **Note**: Pod - Job에 의해 생성된 컨테이너 단위로, 실제 컴퓨팅 리소스를 사용하여 작업 수행
   ```
   kubectl get po -n kbm-u-kubeflow-tutorial
   ```
