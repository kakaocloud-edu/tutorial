# 파이프라인 생성 및 예측 모델 학습
기존 노트북을 활용하여 간단한 계산 파이프라인을 Kubeflow로 실행하고, SDK와 대시보드 UI를 통해 파이프라인을 관리하는 실습입니다. 각 컴포넌트의 입력과 출력, 실행 로그 등을 확인하여 파이프라인의 동작을 이해합니다.

## 1. .ipynb 파일 업로드
1. Notebooks 탭 > `gpu-notebook`의 `CONNECT` 버튼 클릭
2. 좌측 상단의 `+` 클릭
3. Other 중 `Terminal` 선택
4. kubectl.ipynb 파일 다운
    - 터미널에 아래 명령어를 입력하세요.
    #### **lab9-1-4**
    ```bash
    wget https://github.com/kakaocloud-edu/tutorial/raw/main/Kubeflow/src/ipynb/simple_pipeline.ipynb
    ```
    - simple_pipeline.ipynb 파일 생성 확인
5. 필요한 라이브러리 import 
    - simple_pipeline.ipynb 파일 더블 클릭
    - 1번 스크립트 클릭 후 RUN 클릭
6. 대시보드 접속한 로드밸런서의 Public IP 복사
7. Kubeflow Pipelines에 접속하기 위한 환경 변수 설정
    - 아래 환경 변수들에 값들을 넣어주세요.
        - KUBEFLOW_HOST : https://대시보드 접속한 로드밸런서의 Public IP/
        - KUBEFLOW_USERNAME : 대시보드 접속 아이디(이메일) 입력
        - KUBEFLOW_PASSWORD : 대시보드 접속 비밀번호 입력
    - 2번 스크립트 클릭 후 RUN 클릭
8. 컴포넌트 정의 (덧셈 함수를 정의 후 Kubeflow 컴포넌트로 변환)
    - **Note**: ADD 컴포넌트를 정의하는 블록
    -  `3-1`번 스크립트 클릭 후 `RUN` 클릭
9. 컴포넌트 정의 (곱셈 함수를 정의 후 Kubeflow 컴포넌트로 변환)
    - **Note**: Multifly 컴포넌트를 정의하는 블록
    - `3-2`번 스크립트 클릭 후 `RUN` 클릭
10. 두 개의 컴포넌트를 이용하여 파이프라인을 정의
    - **Note**: 두 컴포넌트를 이용해 파이프라인을 정의하는 블록
    - `4`번 확인 후 `RUN` 클릭
11. 파이프라인을 정의한 후 이를 컴파일 하여 YAML 파일로 저장
    - **Note**: 파이프라인을 정의한 후 컴파일하여 yaml 파일로 저장하는 블록
    - `5`번 확인 후 `RUN` 클릭
    - 생성된 `math_pipeline.yaml` 확인
12. 생성된 math_pipeline.yaml 파일 내용 확인하기 
    - 생성된 math_pipeline.yaml 더블 클릭

## 2. SDK를 통한 파이프라인 실행
1. SDK를 통해 파이프라인을 실행
    - **Note**: SDK를 통해 파이프라인을 실행하는 블록
    - `6`번 확인 후 `RUN` 클릭 
    - 파이프라인이 생성되고 실행됨을 확인 
2. `Experiments(KFP)` 탭 > 생성된 math_pipeline_test experiment 확인
3. Runs 탭 > 생성된 `math_pipeline_run` 클릭
4. `Add` 컴포넌트 클릭 후 내용 확인 
5. `Multiply` 컴포넌트 클릭 후 내용 확인

## 3. Kubeflow 대시보드 UI를 통한 파이프라인 실행

1. gpu-notebook > `math.pipeline.yaml` 우클릭 > `Download` 클릭
2. `Pipelines` 탭 > `+ Upload pipeline ` 클릭
3. 파이프라인 생성
    - `Create a new pipeline` 선택
    - Pipeline name : `second math_pipeline`
    - Pipeline description : `this is second math_pipeline`
    - `Upload a file` 선택 후 `Choose file` 클릭하여 다운받은 `math_pipeline.yaml` 업로드
    - Create 클릭
4. `+ Create run` 클릭
5. This run will be associated with the following experiment > `Choose` 클릭
    - Experiment 부분 Choose 클릭
6. Experiment 업로드
    - SDK를 통해 만들어진  math_pipeline test experiment 선택
    - Use this experiment 클릭
7. 파라미터 설정
    - Run parameters
        - `a`: 4
        - `b`: 5
        - `c`: 6 
    - Start 클릭
8. `Experiments(KFP)` 탭 > `math_pipeline test experiment` 클릭
9. 실행되었던 Run 항목들 확인
    - Run의 이름, 상태, Duration, 버전 확인

## 4. 파이프라인 실행 이후 각 항목 확인

### 1. Experiments (KFP)
1. `Experiments(KFP)` 탭 > `math_pipeline test experiment` 클릭
2. 실행되었던 `Run` 항목들 확인
    - Run의 이름, 상태, Duration, 버전 확인
3. 실행된 `Run of second math_pipeline`의 `Pipeline Version` 클릭
4. 실행된 `Run of second math_pipeline`이 참조한 파이프라인 확인
    - 실행된 Run이 참조한 파이프라인을 확인할 수 있음
5. 실행된 `Run of second math_pipeline` 클릭 
6. `Graph` 확인
    - Graph로 각 컴포넌트들과 컴포넌트간의 연결 및 실행 상태를 확인 가능
    - Graph에서 Visualizations,  Events, ML Metadata 등의 정보들도 확인 가능 
7. 각 컴포넌트의 `Graph` - `Input / Output` 클릭 후 정보 확인
    - 컴포넌트에 어떤 파라미터가 입력되었고 출력되었는지 알 수 있음
    - Output에 대한 결과가 Artifacts로 저장되고 그 경로를 볼 수 있음
    - 저장되는 경로는 Object Storage에 생성되어 있는 Bucket > artifacts 폴더 > 관련 네임스페이스 > Run의 Workflow name
8. 각 컴포넌트의 `Graph` - `Detail` 클릭 후 정보 확인 
    - 내부적으로 수행된 Task에 대한 정보들을 확인할 수 있음
        - Task ID
        - Task name
        - Status
        - Started at
        - Finished at
        - Duration
9. 각 컴포넌트의 `Graph` - `Volumes` 정보 확인
    - 마운트 된 볼륨 정보를 확인 가능
10. 각 컴포넌트의 `Graph` - `Logs` 정보 확인
    - 각 컴포넌트들의 로그들 확인 가능
11. 각 컴포넌트의 `Graph` - `Pod` 정보 확인
    - Run이 실제로 실행된 Pod YAML 정보 확인 가능
12. `Config` 선택 후 정보 확인
    - Run에 대한 세부 정보 확인 가능

### 2. Pipelines
1. `Pipelines` 탭 클릭
    - SDK를 활용하여 생성한 파이프라인과 Kubeflow UI 환경에서 생성한 파이프라인 각각을 확인할 수 있음
2. `second math_pipeline` 클릭
3. `Graph` 선택 후 컴포넌트 및 컴포넌트 간 연결 확인
    - 각 컴포넌트들과 컴포넌트 간의 연결을 확인할 수 있음
4. `YAML` 선택 후 Argo Workflows Yaml 형식의 파이프라인 정의 확인
    - Argo Workflows YAML 형식으로 Kubeflow 파이프라인의 정의를 확인 할 수 있음
        - **Note**: 해당 파일은 카카오클라우드의 Object Storage에 생성되어 있는 Bucket > pipeline 폴더에서도 확인 가능

### 3. Artifacts
1. `Artifacts` 탭 클릭
    - 각 Run에 의해서 얻을 수 있었던 결과물 Output 목록을 확인 가능
2. `Pipeline / Workspace`에서 생성한 파이프라인 클릭
3. `Overview` 선택 후 정보 확인
    - 저장 경로와 속성 정보를 확인 가능
4. `Linear Explorer` 선택 후 정보 확인
    - 그래프 형태로 확인 가능

### 4. Artifacts
1. `Executions` 탭 클릭 > `자세히 버튼` 클릭 후 정보 확인
    - Run 내에서 각 작업의 실행 단위 확인 가능(Add, Multiply) 

## 5. 실제 머신러닝 워크플로우를 위한 파이프라인 실습
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 버튼 클릭
2. 좌측 상단의 ` + ` 버튼 클릭
3. Other 중 `Terminal` 클릭
4. `taxi.ipynb` 파일 다운
    - **Note**: 터미널에 아래 명령어를 입력하세요.
    #### **lab8-5-4**
    ```bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/src/ipynb/taxi.ipynb
    ```
    - taxi.ipynb 파일 생성 확인
5. 필요한 라이브러리 import
    - **Note**: 필요한 라이브러리를 import 하는 블록
    - `taxi.ipynb` 파일 더블 클릭
    - 1번 스크립트 클릭 후 `RUN` 클릭
6. Kubeflow Pipelines에 접속하기 위한 환경 변수 설정
    - 아래 환경 변수들에 값들을 넣어주세요.
        - KUBEFLOW_HOST : https://대시보드 접속한 로드밸런서의 Public IP/
        - KUBEFLOW_USERNAME : 대시보드 접속 아이디(이메일) 입력
        - KUBEFLOW_PASSWORD : 대시보드 접속 비밀번호 입력
    - 2번 스크립트 클릭 후 RUN 클릭
8. 파이프라인 컴포넌트 빌드 준비
    - **Note**: 훈련 데이터를 저장할 디렉토리를 준비하는 블록
    - `3`번 확인 후 `RUN` 클릭
9. 데이터 수집 컴포넌트 빌드
    - **Note**: 데이터를 수집 컴포넌트를 빌드하는 블록
    - `3-1`번 확인 후 `RUN` 클릭
10. 예측 모델 학습 컴포넌트
    - **Note**: 예측 모델 학습 컴포넌트를 빌드하는 블록
    - `3-2`번 확인 후 `RUN` 클릭
11. 모델 검증 컴포넌트
    - **Note**: 모델 검증 컴포넌트를 빌드하는 블록
    - `3-3`번 확인 후 `RUN` 클릭
12. 로드 및 생성
    - **Note**: 컴포넌트를 로드 하고 생성하는 블록
    - `4-1`번 확인 후 `RUN` 클릭
13. 파이프라인 정의
    - **Note**: 파이프라인을 정의하는 블록
    - `4-2`번 확인 후 `RUN` 클릭
14. 파이프라인 실행
    - **Note**: 파이프라인을 실행하는 블록
    - `4-3`번 확인 후 `RUN` 클릭
    - 실험이 생성되고 실행되었다는 메세지 확인
15. `Runs` 탭 > `nyc_taxi_pytorch_pipeline_w_cpu run` 클릭
16. NYC Taxi Fare Dataset 컴포넌트 확인
    - `Graph` 선택
    - `NYC Taxi Fare Dataset` 컴포넌트 클릭
    - `Input / Output` 선택 후 하단 내용 확인
17. Train Pytorch Tabular Model 컴포넌트 확인 
    - `Train Pytorch Tabular Model` 컴포넌트 클릭
    - `Input / Output` 선택 후 하단 내용 확인
18. Evaluate Pytorch Tabular Model 컴포넌트 확인
    - `Evaluate Pytorch Tabular Model` 컴포넌트 클릭
    - `Input / Output` 선택 후 하단 내용 확인
