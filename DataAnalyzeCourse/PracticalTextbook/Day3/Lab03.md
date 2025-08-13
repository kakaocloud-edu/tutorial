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
                - Image : `kc-kubeflow-registry/jupyter-tensorflow-cuda-full:v1.8.0.py311.1a`
                - **Note**: 이미지 이름 정확하게 확인하기
        - CPU/RAM
            - Minimum CPU : `2`
            - Minimum memory  Gi : `8`
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


## 2. 생성된 Notebook에 접속하여 namespace 내의 리소스들 확인
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. kubectl.ipynb 파일 다운로드
   #### **Lab5-2-5**
   ```bash
   wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/ipynb/kubectl.ipynb
   ```
   - kubectl.ipynb 파일 생성 확인 및 더블 클릭 후 내부 코드 실행

## 3. 간단한 Notebook 실습
1. speed.ipynb 파일 다운로드
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력

   #### **lab4-3-6**
   ```bash
   wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/ipynb/speed.ipynb
   ```
   - speed.ipynb 파일 생성 확인 및 더블 클릭 후 내부 코드 실행

2. speed 생성 확인

## 4. Notebook에서 Object Storage에 쌓인 데이터 확인
1. data_check.ipynb 파일 다운로드
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력

   #### **lab4-3-6**
   ```bash
   wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/ipynb/data_check.ipynb
   ```

   - kubectl.ipynb 파일 생성 확인 및 더블 클릭 후 내부 코드 실행

2. data 생성 확인

## 5. Notebook에서 전처리 진행
1. preprocessed_user_behavior_prediction.ipynb 파일 다운로드
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력

   #### **lab4-3-6**
   ```bash
   wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/ipynb/preprocessed_user_behavior_prediction.ipynb
   ```

   - preprocessed_user_behavior_prediction.ipynb 파일 생성 확인 및 더블 클릭 후 내부 코드 실행

2. processed_user_behavior.csv 확인
3. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage
4. data-catalog-bucket 클릭
5. preprocessed_user_behavior_prediction.parquet 적재 확인
    - **Note**: /data-catalog-dir/preprocessed/preprocessed_user_behavior_prediction.parquet 확인
