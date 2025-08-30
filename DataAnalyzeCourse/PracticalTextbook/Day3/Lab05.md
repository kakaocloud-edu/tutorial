# 성별 추론 모델 파이프라인 실습

실시간 정제된 데이터를 기반으로 하는 성별 예측 모델 학습 과정을 파이프라인으로 진행하는 실습입니다.

## 1. 성별 추론 모델 파이프라인 실습 준비 (2분)
- **Note**: 성별 추론 모델 노트북 실습은 [Lab05_etc.md](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/PracticalTextbook/Lab05_etc.md) 참고
1. 카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
2. `api-lb` 로드밸런서의 Public IP를 복사 후 클립보드에 저장
3. gender_tableJoin.ipynb 파일 더블 클릭 후 실행
    - 실행 버튼(Shift + Enter)을 눌러 셀 실행
4. 환경 구성
    - 실습에 필요한 라이브러리와 경로, 네트워크 설정 값 등을 설정
    - 아래 환경 변수에 ‘api-lb의 Public IP’ 를 삽입
        - BASE_URL = "http://**{api-lb의 Public IP}**”
5. Product -> Category Mapping 테이블 생성
    - product_id 에 맞는 category를 Mapping해서 테이블로 저장
6. Keyword -> Category Mapping 테이블 생성
    - search_keyword 에 맞는 category를 Mapping해서 테이블로 저장
7. Mapping 테이블들과 원본 테이블 Join
    - 위에서 생성한 Mapping 테이블들과 원본 테이블을 Join
    - datasets/gender 경로에 Join table 저장 확인
    - 이후 성별 추론 실습에서 Join 테이블을 원본 데이터로 사용

## 2. 성별 추론 모델 파이프라인 실습 진행 (10분)

1. Katib 하이퍼파라미터 튜닝 & 최적 하이퍼파라미터 값 추출
    - **Note**: lab3에서 생성한 Notebook(`cpu-notebook`) `Terminal`에서 입력
    - Katib 하이퍼파라미터 튜닝 experiment 적용 및 실행
    
    ### **Lab5-2-10**
    
    ```
    kubectl -n kbm-u-kubeflow-tutorial apply -f gender_experiment.yaml
    ```
    
    - experiment 생성된 것을 확인
        
        <img width="992" height="50" alt="Image" src="https://github.com/user-attachments/assets/343d72d0-4e5e-414c-97c0-a965cfec4a12" />
        
2. Kubeflow Dashboard 이동하여 Katib Experiments 탭 클릭
   - 생성된 gender-logistic-random 클릭
    - Katib 하이퍼파라미터 튜닝 진행 상황 확인
    - Status 값이 Experiment has succeeded because max trial count has reached 가 뜨면 튜닝 성공
    - Best trial's params에서 Katib이 찾은 최적의 하이퍼파라미터 값 확인
            
   <img width="1547" height="32" alt="Image" src="https://github.com/user-attachments/assets/ca332ced-2034-4644-a8be-a2ff1f5e1019" />
            
2. gender_pipeline.ipynb 파일 더블 클릭 후 실행
    - gender_pipeline.ipynb 파일 좌측 상단에 있는 실행 버튼(Shift + Enter)을 눌러 셀 실행
3. 환경 구성
    - 파이프라인을 가동하기 위한 패키지를 설치하고 컴포넌트와 파이프라인을 정의
4. 공통 파라미터 초기화 컴포넌트
    - 파이프라인에서 사용하는 공통 파라미터들을 초기화하는 컴포넌트를 정의
5. 로그인 전 구간 필터링 컴포넌트
    - PVC에 있는 Join된 원본 데이터를 읽고 로그인 전 구간을 필터링 하는 컴포넌트를 정의
6. 피처 집계 & 성별 라벨링 컴포넌트
    - 로그인 전 로그를 세션 단위로 집계하 성별 라벨을 붙여 학습용 데이터를 생성하는 컴포넌트를 정의
7. 카운트 & 파생 컬럼 생성 컴포넌트
    - 카테고리 등장 횟수를 저장하는 카운트 컬럼, 횟수를 비율로 치환하는 파생 컬럼을 생성하는 컴포넌트를 정의
8. 최종 학습 데이터 셋 생성 컴포넌트
    - 카운트 & 파생 컬럼과 라벨을 합쳐 최종 학습용 데이터 셋을 저장하는 컴포넌트를 정의
9. 데이터 셋 분할 컴포넌트
    - 최종 데이터 셋을 학습용 / 검증용 데이터 셋으로 분할하는 컴포넌트를 정의
10. Logistic 모델 학습 컴포넌트
    - Logistic 모델을 학습하는 컴포넌트를 정의합니다.
11. 모델 검증 및 평가 컴포넌트
    - 학습한 모델을 검증하여 평가하는 컴포넌트를 정의
12. Katib 최적 하이퍼파라미터 로드 컴포넌트
    - Katib에서 최적 하이퍼파라미터를 로드하는 컴포넌트를 정의
13. 모델 재학습 컴포넌트
    - katib에서 찾은 최적 하이퍼파라미터를 적용해 모델을 재학습하는 컴포넌트를 정의
14. 모델 검증 및 평가 컴포넌트
    - Katib 최적 하이퍼파라미터로 학습한 모델을 검증 및 평가하는 컴포넌트를 정의
15. Object Storage에 모델 저장 컴포넌트
    - 검증 및 평가된 모델을 Object Storage에 저장하는 컴포넌트를 정의
16. KServe 모델 배포 컴포넌트
    - Object Storage에 저장된 모델을 KServe InferenceService로 배포하는 컴포넌트를 정의
17. 파이프라인 정의
    - 컴포넌트들을 연결하여 파이프라인을 정의하고 컴파일
    - 좌측 gender_pipeline.yaml 파일 생성 확인
18. gender_pipeline.yaml 파일 위에서 마우스 우클릭 후 Download
19. Kubeflow Dashboard > Pipelines > Pipelines
20. 우측 상단 `+ Upload pipeline` 버튼 클릭
    - `Create a new pipeline` 체크
    - `Private` 체크
    - Pipeline Name : `gender_pipeline`
    - Pipeline Description : `빈 칸`
    - `Upload a file` 체크
        - `Choose file` 버튼 클릭
        - `gender_pipeline.yaml` 파일 다운로드 받은 경로로 가서 선택 후 열기
    - `Create` 버튼 클릭
21. 우측 상단 `+ Create experiment` 버튼 클릭
    - Experiment name : `gender_predict`
    - Experiment Description : `빈 칸`
    - `Next` 버튼 클릭
22. Run 설정 값 입력
    - Pipeline : `gender_pipeline`
    - Pipeline Version : `gender_pipeline`
    - Run name : `Run of gender_pipeline`
    - Description : `빈 칸`
    - Experiment : `gender_predict`
    - Service Account : `빈 칸`
    - Run Type : `One-off`
    - Custom Pipeline Root : `체크 해제`
    - Run parameters : `Default 값`
        - **note :** 아래 3개의 입력에만 값 입력
        - kakao_access_key - string : `{S3_ACCESS_KEY_ID}`
        - kakao_public_read - boolean : `true`
        - kakao_secret_key - string : `{S3_SECRET_ACCESS_KEY}`
    - `Start` 버튼 클릭
23. 파이프라인 그래프 탭에서 진행 상황을 확인
    - Runs name 옆 Executed successfully이 되면 진행 완료
24. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
25. `models` 버킷 생성 확인 및 클릭
26. 버킷 안 `gender_predict_pipeline` 폴더 생성 확인 및 클릭
27. 저장된 `model.joblib` 파일 확인
28. Kubeflow Dashboard 이동하여 KServe Endpoints 탭 클릭
    - 생성된 `gender-sklearn` 클릭
29. 배포된 모델 정보 확인
30. `cpu-notebook`의 gender_pipeline.ipynb에서 모델 추론 실습 (Cell 15) 진행
    - KServe로 배포된 모델에 샘플 데이터를 입력하여 추론하는 실습
    - 실제 결과와 예측 결과를 비교
