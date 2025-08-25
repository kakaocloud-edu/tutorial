# K8s의 내부 동작 확인

쿠버네티스 위에서 동작하는 Kubeflow의 리소스들이 어떤 것들이 있는지 확인해 보는 실습입니다.

## 1. CPU 기반 Notebook 생성 (약 3분 소요)

- **Note** : Kubeflow 콘솔에서 진행하는 실습입니다.
1. kbm-u-kubeflow-tutorial 네임스페이스 선택 > 좌측 메뉴바의 `Notebooks` 탭 클릭
2. `+ New Notebook` 클릭
    - 노트북 설정 정보
        - Name
            - Name : `cpu-notebook`
        - Docker Image
            - `Custom Notebook` 클릭
                - Image : `kc-kubeflow-registry/jupyter-tensorflow-cuda-full:v1.10.0.py311.1a`
                - **Note**: 이미지 이름 정확하게 확인하기
        - CPU/RAM
            - Minimum CPU : `2`
            - Minimum memory Gi : `8`
        - GPUs
            - Number of GPUs : `None`
        - Workspace Valume, Data Valumes : `모두 기본값 사용`
        - `Advanced Options` 클릭
            - Configurations : `기본값 사용`
            - Affinity Config : `pool-worker`
            - Tolerations Group : `None`
            - Miscellaneous Settings : `Enable Shared Memory`
    - `LAUNCH` 클릭
3. Notebook 생성 확인

## 2. namespace 내의 리소스 확인

1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. 실습에 필요한 ipynb 파일들 다운로드
    
    ### **Lab3-2-3**
    
    ```bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab03/kubectl.ipynb \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab03/speed.ipynb \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab03/data_check.ipynb \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab04/sessionDrop_predict.ipynb \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab04/next_state.ipynb \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab05/gender_tableJoin.ipynb \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab05/gender_predict.ipynb \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab05/gender_train.py \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab05/gender_experiment.yaml \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab05/KServe.ipynb
    ```
    
    - 아래 사진과 같은 파일들 생성 확인


4.  kubectl.ipynb 실행 
    - 실행 버튼(Shift + Enter)을 눌러 셀 실행


## 3. 간단한 Notebook 실습

CIFAR-10 이미지를 분류하는 간단한 CNN을 학습하고 성능을 평가·시각화하는 Notebook 실습입니다.

1. speed.ipynb 파일 실행
    - 실행 버튼(Shift + Enter)을 눌러 셀 실행
    - 진행 상황 확인

## 4. Object Storage에 쌓인 데이터 확인

1. data_check.ipynb 파일 실행
    - 실행 버튼(Shift + Enter)을 눌러 셀 실행
3. 필요한 라이브러리 설치
4. Delta Lake에서 현재 스냅샷 로드 → 정렬 후 CSV/Parquet 저장
    - 아래 환경 변수에 S3 키 값 삽입
        - S3_ACCESS_KEY = **{S3_ACCESS_KEY_ID}**
        - S3_SECRET_KEY = **{S3_SECRET_ACCESS_KEY}**
5. datasets 폴더 더블 클릭 후 원본 데이터 로드 확인
