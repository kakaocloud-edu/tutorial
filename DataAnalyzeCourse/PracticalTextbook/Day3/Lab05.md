# 성별 추론 모델 배포 및 추론 실습

실시간 정제된 데이터를 기반으로 하는 성별 예측 모델 학습 과정입니다. 전처리 데이터로 학습 및 검증을 마친 성별 추론 모델을  Object Storage에 저장하고 KServe를 이용하여 모델을 배포합니다. 이후 배포된 모델에 샘플 데이터를 입력하여 성별 추론을 진행하는 실습입니다.

## 1. 성별 추론 모델 학습 준비 (2분)
1.  카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
2. `api-lb`  로드밸런서의 Public IP를 복사 후 클립보드에 저장
3.  gender_tableJoin.ipynb 파일 더블 클릭 후 실행
    -  \실행 버튼(Shift + Enter)을 눌러 셀 실행
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

## 2. 성별 추론 모델 학습 진행 (7분)

1. gender_predict.ipynb 파일 더블 클릭 후 실행
    - gender_predict.ipynb 파일 좌측 상단에 있는 실행 버튼(Shift + Enter)을 눌러 셀 실행
2. 환경 구성
    - 실습을 원활하게 진행하기 위해 라이브러리와 경로, 상수 값 등을 설정
3. 원본 데이터 로드 & 로그인 전 구간 추출
    - 원본과 매핑 테이블을 조인한 데이터를 원본 데이터로 로드
    - 사용자의 로그인 전 행동 패턴을 분석해야 하므로 로그인 전 구간 추출
4. Target Label 생성 & 로그인 전 구간 수치 집계
    - 실제 결과 값인 `Label` 생성
    - 로그인 완료한 세션 수 집계 
5. 카테고리 카운트 & 파생 컬럼 생성 (Feature Engineering)
    - 카테고리 등장 횟수를 저장하는 카운트 컬럼 생성
    - 등장 횟수를 비율로 치환한 파생 컬럼 생성
6. 파생 컬럼 결합 및 저장 (Feature Engineering)
    - 카운트, 파생 컬럼 결합하여 저장
    - 저장한 전처리 데이터로 모델 학습
7. 학습용 / 검증용 데이터셋 분할
    - 모델을 학습하기 위한 학습용 / 모델을 검증하기 위한 검증용 데이터 셋으로 분할
8. 모델 학습
    - 학습용 데이터 셋으로 모델 학습
9. 학습 평가
    - 검증용 데이터 셋으로 모델을 검증 및 평가
    - 평가에서 `Macro-F1`, `Accuracy` 값 확인
10. Katib 하이퍼파라미터 튜닝 & 최적 하이퍼파라미터 값 추출

    - **Note**: lab3에서 생성한 Notebook(`cpu-notebook`) `Terminal`에서 입력
    - Katib 하이퍼파라미터 튜닝 experiment 적용 및 실행
    #### **Lab5-2-10**
    ```
    kubectl -n kbm-u-kubeflow-tutorial apply -f gender_experiment.yaml
    ```
    
    - experiment 생성된 것을 확인
        
        <img width="992" height="50" alt="Image" src="https://github.com/user-attachments/assets/343d72d0-4e5e-414c-97c0-a965cfec4a12" />
        
    - Kubeflow Dashboard 이동하여 Katib Experiments 탭 클릭
        - 생성된 gender-logistic-random 클릭
        - Katib 하이퍼파라미터 튜닝 진행 상황 확인
        - Status 값이 Experiment has succeeded because max trial count has reached 가 뜨면 튜닝 성공
        - Best trial's params에서 Katib이 찾은 최적의 하이퍼파라미터 값 확인
            
            <img width="1547" height="32" alt="Image" src="https://github.com/user-attachments/assets/ca332ced-2034-4644-a8be-a2ff1f5e1019" />
            
12.  `cpu-notebook`의 gender_predict.ipynb에서 Katib 하이퍼파라미터 추출 값 확인
        - **note:** Cell 9번 부터 실행
        - Katib에서 찾은 최적 하이퍼파라미터 값 확인
13. Katib 최적 하이퍼파라미터로 모델 학습
    - Katib 최적 하이퍼파라미터로 모델 재학습
14. Katib 모델 평가 밎 저장
    - Katib 모델 평가 값 확인 및 저장
    - 일반 학습한 모델 평가 값과 Katib 최적 하이퍼파라미터로 학습한 모델 평가 값 비교
15. 성별 추론 결과 값 시각화
    - Katib 최적 하이퍼파라미터로 추론한 결과 값을 그래프로 확인
    - 예측 성공 → 초록색 / 예측 실패 → 빨간색


## 3. Object Stroage에 모델 저장 후 KServe로 모델 배포 (2분)

1. KServe.ipynb 파일 더블 클릭 후 실행
    - 실행 버튼(Shift + Enter)을 눌러 셀 실행
2. 패키지 설치
    - 실습에 필요한 패키지를 설치
3.  Object Storage에 모델 저장
    - Kakaocloud Object Storage에 모델을 저장
    - 아래 환경 변수들에 S3 키 값을 삽입 후 실행
        - AWS_ACCESS_KEY_ID = "**{S3_ACCESS_KEY}**”
        - AWS_SECRET_ACCESS_KEY = "**{S3_SECRET_KEY}**”
4. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
5. `models`  버킷 생성 확인 및 클릭
6. 버킷 안 `gender_predict` 폴더 생성 확인 및 클릭
7. 저장된 `model.joblib` 파일 확인
8. `cpu-notebook` 내 `kserve_s3_creds.env` 파일 생성 확인
9. KServe 리소스 생성
    - KServe가 Object Storage에 있는 모델을 읽기 위한 리소스를 생성
    - notebook 내 `kserve_sa.env` 파일 생성 확인
10. KServe InferenceService 생성 및 모델 배포
    - 배포된 모델을 API를 활용하여 사용할 수 있는 KServe InferenceService 생성
    - KServe InferenceService 생성 확인
    
    <img width="315" height="19" alt="Image" src="https://github.com/user-attachments/assets/e1d214f8-e110-431f-ad6c-854827c745e8" />
    
11. `cpu-notebook`의 `terminal` 클릭
12. 배포된 모델을 확인하는 kubectl 명령어 실행 
    
    #### **Lab5-3-12**
    
    ```
    kubectl get isvc -n kbm-u-kubeflow-tutorial gender-predict -w
    ```
    
    <img width="858" height="38" alt="Image" src="https://github.com/user-attachments/assets/3a25c854-e913-40d7-a098-e9ce768733ff" />
    
 13. Kubeflow Dashboard 이동하여 KServe Endpoints 탭 클릭
 14. 생성된 `gender-predict` 클릭
 15. 배포된 모델 정보 확인

## 4. 모델 성별 추론 실습 진행 (1분)

1. KServe.ipynb 파일 실행
    - **note:** Cell 5번 부터 실행
    - KServe를 이용하여 배포된 모델 API URL 확인
    - Cell 내의 10개의 샘플 데이터 확인
2. 출력된 추론 결과 값을 확인
   - 실제 결과와 예측 결과를 비교
