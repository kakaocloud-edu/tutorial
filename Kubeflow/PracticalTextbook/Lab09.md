# 파이프라인 생성 및 예측 모델 학습
기존 노트북을 활용하여 간단한 계산 파이프라인을 Kubeflow로 실행하고, SDK와 대시보드 UI를 통해 파이프라인을 관리하는 실습입니다. 각 컴포넌트의 입력과 출력, 실행 로그 등을 확인하여 파이프라인의 동작을 이해합니다.

## 1. .ipynb 파일 업로드
1. Notebooks 탭 > gpu-notebook > `CONNECT` 버튼 클릭
2. 좌측 상단의 `+` 클릭
3. Notebook에서 `Terminal` 선택
4. kubectl.ipynb 파일 다운
    - 터미널에 아래 명령어를 입력하세요.
     #### **lab9-1-4**
   ```bash
   wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/simple_pipeline.ipynb
   ```
    - simple_pipeline.ipynb 파일 생성 확인

5. 필요한 라이브러리 import 
    - simple_pipeline.ipynb 파일 더블 클릭
    - 1번 스크립트 클릭 후 RUN 클릭
6. 대시보드 접속한 로드밸런서의 Public Ip 복사
7. Kubeflow Pipelines에 접속하기 위한 환경 변수 설정
    - 아래 환경 변수들에 값들을 넣어주세요.

   `KUBEFLOW_HOST`: http://대시보드 접속한 로드밸런서의 Public IP/

   `KUBEFLOW_USERNAME`: 대시보드 접속 아이디(이메일) 입력
   
   `KUBEFLOW_PASSWORD`: 대시보드 접속 비밀번호 입력
   
   - 2번 스크립트 클릭 후 RUN 클릭

9. 컴포넌트 정의 (덧셈 함수를 정의 후 Kubeflow 컴포넌트로 변환) 
    - `3-1`번 스크립트 클릭 후 `RUN` 클릭

10. 컴포넌트 정의 (곱셈 함수를 정의 후 Kubeflow 컴포넌트로 변환)
    - `3-2`번 스크립트 클릭 후 `RUN` 클릭

11. 두 개의 컴포넌트를 이용하여 파이프라인을 정의
    - `4`번 확인 후 `RUN` 클릭

12. 파이프라인을 정의한 후 이를 컴파일 하여 YAML 파일로 저장 
    - `5`번 확인 후 `RUN` 클릭
    - 생성된 `math_pipeline.yaml` 확인
  
## 2. SDK를 통한 파이프라인 실행

1. SDK를 통해 파이프라인을 실행
    - `6`번 확인 후 `RUN` 클릭 
    - 파이프라인이 생성되고 실행됨을 확인 
2. Notebooks 탭 > Experiments (KFP) > 생성된 math_pipeline_test experiment 확인
3. Notebooks 탭 > Runs > 생성된 `math_pipeline_run` 클릭
4. `Add` 컴포넌트 클릭 후 내용 확인 
5. `Multiply` 컴포넌트 클릭 후 내용 확인

## 3. Kubeflow 대시보드 UI를 통한 파이프라인 실행

1. gpu-notebook > `math.pipeline.yaml` 우클릭 > `Download` 클릭
2. Notebooks 탭 > Pipelines > `+ Upload pipeline ` 클릭
3. 파이프라인 생성
    - `Create a new pipeline` 선택
    - `Pipeline name`: second math_pipeline
    - `Pipeline description`: this is second math_pipeline
    - `Upload a file` 선택 후 `Choose file` 클릭하여 다운받은 `math_pipeline.yaml` 업로드
4. `+ Create run` 클릭
5. `This run will be associated with the following experiment` > `Choose` 클릭
6. Experiment 업로드
    - SDK를 통해 만들어진  math_pipeline test experiment 선택
    - Experiment 부분 Choose 클릭
7. 파라미터 설정
    - `a`: 4
    - `b`: 5
    - `c`: 6 
    - `Start` 선택
8. Notebooks 탭 > Experiments(KFP) > `math_pipeline test experiment` 클릭
9. 실행되었던 Run 항목들 확인 

## 4. 파이프라인 실행 이후 각 항목 확인

### 1. Experiments (KFP)
1. Notebooks 탭 > `Experiments(KFP)` > `math_pipeline test experiment` 클릭
2. 실행되었던 `Run` 항목들 확인
3. 실행된 `Run of second math_pipeline`의 `Pipeline Version` 클릭
4. 실행된 `Run of second math_pipeline`이 참조한 파이프라인 확인
5. 실행된 `Run of second math_pipeline` 클릭 
6. `Graph` 선택 후 각 컴포넌트들과 컴포넌트간의 연결 및 실행 상태를 확인 
7. 각 컴포넌트의 `Graph` - `Input / Output` 클릭 후 정보 확인 
8. 각 컴포넌트의 `Graph` - `Detail` 클릭 후 정보 확인 
9. 각 컴포넌트의 `Graph` - `Volumes` 정보 확인 
10. 각 컴포넌트의 `Graph` - `Logs` 정보 확인 
11. 각 컴포넌트의 `Graph` - `Pod` 정보 확인 
12. `Config` 선택 후 정보 확인

### 2. Pipelines
1. Notebooks 탭 > `Pipelines` 클릭
2. `second math_pipeline` 클릭
3. `Graph` 선택 후 컴포넌트 및 컴포넌트 간 연결 확인
4. `YAML` 선택 후 Argo Workflows Yaml 형식의 파이프라인 정의 확인

### 3. Artifacts
1. Notebooks 탭 > `Artifacts` 클릭
2. `Pipeline / Workspace`에서 생성한 파이프라인 클릭
3. `Overview` 선택 후 정보 확인
4. `Linear Explorer` 선택 후 정보 확인

### 4. Artifacts
1. Notebooks 탭 > `Executions 클릭` > `자세히 버튼` 클릭 후 정보 확인 

## 5. 실제 머신러닝 워크플로우를 위한 파이프라인 실습
1. Notebooks 탭 > `cpu-notebook` > `CONNECT` 버튼 클릭
2. 좌측 상단의 ` + ` 버튼 클릭
3. Notebook에서 `Terminal`선택
4. `taxi.ipynb` 파일 다운
    - 터미널에 아래 명령어를 입력하세요.
     #### **lab9-5-4**
   ```bash
   wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/taxi.ipynb
   ```
    - taxi.ipynb 파일 생성 확인
5. 필요한 라이브러리 import 
    - `taxi.ipynb` 파일 더블 클릭
    - `1`번 스크립트 클릭 후 `RUN` 클릭
6. Kubeflow Pipelines에 접속하기 위한 환경 변수 설정
    - 아래 환경 변수들에 값들을 넣어주세요.
   
   `KUBEFLOW_HOST`: http://대시보드 접속한 로드밸런서의 Public IP/
   
   `KUBEFLOW_USERNAME`: 대시보드 접속 아이디(이메일) 입력
   
   `KUBEFLOW_PASSWORD`: 대시보드 접속 비밀번호 입력
   
   - `2`번 스크립트 클릭 후 `RUN` 클릭
8. 파이프라인 컴포넌트 빌드 준비
    - `3`번 확인 후 `RUN` 클릭
9. 데이터 수집 컴포넌트 빌드
    - `3-1`번 확인 후 `RUN` 클릭
10. 예측 모델 학습 컴포넌트
    - `3-2`번 확인 후 `RUN` 클릭
11. 모델 검증 컴포넌트
    - `3-3`번 확인 후 `RUN` 클릭
12. 로드 및 생성
    - `4-1`번 확인 후 `RUN` 클릭
13. 파이프라인 정의
    - `4-2`번 확인 후 `RUN` 클릭
14. 파이프라인 실행
    - `4-3`번 확인 후 `RUN` 클릭
    - 실험이 생성되고 실행되었다는 메세지 확인
15. Notebooks 탭 > `Runs` > `nyc_taxi_pytorch_pipeline_w_cpu run` 클릭
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


