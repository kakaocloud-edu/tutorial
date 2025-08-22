# 성별 추론 모델 학습

실시간 정제된 데이터를 기반으로 하여 사용자의 성별을 추론하는 모델 학습 과정입니다.

## 1. Notebook에서 성별 추론 모델 학습 준비 (2분)
성별 추론 실습 전 필요한 Mapping 테이블을 생성하여 원본 테이블과 Join하는 예제입니다.

1.  카카오 클라우드 콘솔 > Beyond Networking Service > Load Balancing
2. `api-lb`  로드밸런서의 Public IP를 복사 후 클립보드에 저장
3. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
4. Other 중 `Terminal` 클릭
5. gender_tableJoin.ipynb 파일 다운로드
    
    ### **Lab4-1-3**
    
    ```bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab04/gender_tableJoin.ipynb
    
    ```
    
    - gender_tableJoin.ipynb 파일 생성 확인
6. gender_predict.ipynb 파일 더블 클릭
    - gender_predict.ipynb 파일 좌측 상단에 있는 실행 버튼(Shift + Enter)을 눌러 셀 실행
7. 공통 셋업 & 유틸
    - 실습에 필요한 라이브러리와 경로, 네트워크 설정 값 등을 설정
    - 아래 환경 변수에 ‘api-lb의 Public IP’ 를 삽입
        - BASE_URL = "http://**{api-lb의 Public IP}**”
8. Product -> Category Mapping 테이블 생성
    - product_id 에 맞는 category를 Mapping해서 테이블로 저장
9. Keyword -> Category Mapping 테이블 생성
    - search_keyword 에 맞는 category를 Mapping해서 테이블로 저장
10. Mapping 테이블들과 원본 테이블 Join
    - 위에서 생성한 Mapping 테이블들과 원본 테이블을 Join
    - 이후 성별 추론 실습에서 Join 테이블을 원본 데이터로 사용

## 2. Notebook에서 성별 추론 모델 학습 진행 (10분)

사용자의 로그인 전 행동 패턴을 보고 사용자의 성별을 추론하는 실습입니다.

1. 노트북 상단  `Terminal`   탭 클릭
2. gender_predict.ipynb 파일 다운로드
    
    ### **Lab4-2-2**
    
    ```bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab04/gender_predict.ipynb
    ```
    
    - gender_predict.ipynb 파일 생성 확인
3. gender_predict.ipynb 파일 더블 클릭
    - gender_predict.ipynb 파일 좌측 상단에 있는 실행 버튼(Shift + Enter)을 눌러 셀 실행
4. 환경 구성
    - 실습을 원활하게 진행하기 위해 라이브러리와 경로, 상수 값 등을 설정
5. 원본 데이터 로드 & 로그인 전 구간 추출
    - 원본과 매핑 테이블을 조인한 데이터를 읽어와 로그인 전 구간을 추출
    - 사용자의 로그인 전 행동 패턴을 분석해야 하므로 로그인 전 구간 추
6. Target Label 생성 & 로그인 전 구간 수치 집계
    - 실제 결과 값인 `Label` 생성
    - 로그인 완료한 세션 수 집
7. 카테고리 카운트 & 파생 컬럼 생성 (Feature Engineering)
    - 카테고리 등장 횟수를 저장하는 카운트 컬럼 생성
    - 등장 횟수를 비율로 치환한 파생 컬럼 생성
8. 파생 컬럼 결합 및 저장 (Feature Engineering)
    - 카운트, 파생 컬럼 결합하여 저장
    - 저장한 전처리 데이터로 모델 학습
9. 학습용 / 검증용 데이터셋 분할
    - 모델을 학습하기 위한 학습용 / 모델을 검증하기 위한 검증용 데이터 셋으로 분할
10. 모델 학습
    - 학습용 데이터 셋으로 모델 학습
11. 학습 평가
    - 검증용 데이터 셋으로 모델을 검증 및 평가
    - 평가에서 `Macro-F1`, `Accuracy` 값 확인
12. Katib 하이퍼파라미터 튜닝 & 최적 하이퍼파라미터 값 추출
    - 노트북 상단  `Terminal`  탭 클릭
    - gender_train.py 다운로드
    
    ```
    bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab04/gender_train.py
    ```
    
    - gender_experiment.yaml 파일 다운로드
    
    ```
    bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab04/gender_experiment.yaml
    ```
    
    - Katib 하이퍼파라미터 튜닝 experiment 적용 및 실행
    
    ```
    jsx
    kubectl -n kbm-u-kubeflow-tutorial apply -f gender_experiment.yaml
    ```
    
    - experiment 생성된 것을 확인
        
        ![yaml파일적용사진.png](attachment:a5fc5942-d6e3-44ce-8f08-1c16bfd18ba9:yaml파일적용사진.png)
        
    - Kubeflow Dashboard 이동하여 Katib Experiment 탭 클릭
        - 생성된 gender-logistic-random 클릭
        - Katib 하이퍼파라미터 튜닝 진행 상황 확인
        - Status 값이 Experiment has succeeded because max trial count has reached 가 뜨면 튜닝 성공
        - Best trial's params에서 Katib이 찾은 최적의 하이퍼파라미터 값 확인
            
            ![katib최적하이퍼파라미터사진.png](attachment:36c2477f-46bf-402d-9350-dd4e29d83c18:katib최적하이퍼파라미터사진.png)
            
13.  Jupyter notebook에서 Katib 하이퍼파라미터 튜닝 & 추출 값 확인
 **note:** Cell 9번 부터 실행
    - Katib에서 찾은 최적 하이퍼파라미터 값 확인
14. Katib 최적 하이퍼파라미터로 모델 학습
    - Katib 최적 하이퍼파라미터로 모델 재학습
15. Katib 모델 평가 밎 저장
    - Katib 모델 평가 값 확인 및 저장
    - 일반 학습한 모델 평가 값과 Katib 최적 하이퍼파라미터로 학습한 모델 평가 값 비교
16. 성별 추론 결과 값 시각화
    - Katib 최적 하이퍼파라미터로 추론한 결과 값을 그래프로 확인
    - 예측 성공 → 초록색 / 예측 실패 → 빨간색
