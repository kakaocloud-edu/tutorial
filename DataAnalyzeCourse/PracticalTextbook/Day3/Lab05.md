# 모델 배포 및 추론 실습

전처리 데이터 학습 후 검증을 마친 성별 추론 모델을  Object Storage에 저장하고 KServe를 이용하여 모델을 배포합니다. 배포된 모델에 샘플 데이터를 입력하여 성별 추론을 진행하는 실습입니다.

## 1. Object Stroage에 모델 저장 후 KServe로 모델 배포 (2분)

1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. KServe.ipynb 파일 다운로드

    #### **Lab5-1-3**

    ```
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab05/KServe.ipynb
    ```

    - KServe.ipynb 파일 생성 확인
4. KServe.ipynb 파일 더블 클릭
    - KServe.ipynb 파일 좌측 상단에 있는 실행 버튼(Shift + Enter)을 눌러 셀 실행
5. 패키지 설치
    - 실습에 필요한 패키지를 설치
6.  Object Storage에 모델 저장
    - Kakaocloud Object Storage에 모델을 저장
    - 아래 환경 변수들에 S3 키 값을 삽입 후 실행
        - AWS_ACCESS_KEY_ID = "**{S3_ACCESS_KEY}**”
        - AWS_SECRET_ACCESS_KEY = "**{S3_SECRET_KEY}**”
    - 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
    - `models`  버킷 생성 확인 및 클릭
    - 버킷 안 `gender_predict` 폴더 생성 확인 및 클릭
    - 저장된 `model.joblib` 파일 확인
    - notebook 내 `kserve_s3_creds.env` 파일 생성 확인
7. KServe 리소스 생성
    - KServe가 Object Storage에 있는 모델을 읽기 위한 리소스를 생성
    - notebook 내 `kserve_sa.env` 파일 생성 확인
8. KServe InferenceService 생성 및 모델 배포
    - 배포된 모델을 API를 활용하여 사용할 수 있는 KServe InferenceService 생성
    - KServe InferenceService 생성 확인
    
    <img width="315" height="19" alt="Image" src="https://github.com/user-attachments/assets/e1d214f8-e110-431f-ad6c-854827c745e8" />
    
9. 배포된 모델 확인
    - 노트북 상단  `Terminal`   탭 클릭
    - kubectl 명령어를 통해 배포된 모델 확인
    
    #### **Lab5-1-9**
    
    ```
    kubectl get isvc -n kbm-u-kubeflow-tutorial gender-predict -w
    ```
    
    <img width="858" height="38" alt="Image" src="https://github.com/user-attachments/assets/3a25c854-e913-40d7-a098-e9ce768733ff" />
    
    - Kubeflow Dashboard 이동하여 KServe Endpoints 탭 클릭
        - 생성된 `gender-predict` 클릭
        - 배포된 모델 정보 확인

## 2. 모델 성별 추론 실습 진행 (1분)

1. 좌측 상단 실행 버튼(Shift + Enter)을 눌러 성별 추론 셀 (Cell 5) 을 실행
    - KServe를 이용하여 배포된 모델 API URL 확인
    - Cell 내의 10개의 샘플 데이터 확인
2. 출력된 추론 결과 값을 확인
   - 실제 결과와 예측 결과를 비교
