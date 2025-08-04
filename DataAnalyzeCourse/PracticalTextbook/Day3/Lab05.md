# 간단한 Notebook 실습
   - **Note** : Kubeflow 콘솔에서 진행하는 실습입니다.

CPU, GPU Notebook을 각각 생성하고 Tensorboard, 하이퍼파라미터 튜닝 등을 실습합니다.

## 1. GPU 기반 Jupyter Notebook 생성 (약 3분 소요)
1. kbm-u-kubeflow-tutorial 네임스페이스 선택 > 좌측 메뉴바의 Notebooks 탭 클릭
2. `+ New Notebook` 클릭
   - 노트북 설정 정보
      - Name
         - Name : `gpu-notebook`
         - Namespace : `kbm-u-kubeflow-tutorial`
      - Docker Image
         -  Image : `mlops-pipelines/jupyter-tensorflow-cuda-full:v1.0.1.py36`
         -  **Note**: 이미지 이름 정확하게 확인하기
      - CPU/RAM
         - Requested CPUs : `2`
         - Requested memory in Gi : `8`
      - GPUs
         - Number of GPUs : `4` 
         - GPU Vendor : `NVIDIA MIC - 1g.10gb`  
      - Workspace Valume, Data Valumes, Configurations : `모두 기본값 사용`
      - Affiinity/Tolerations
         - Affinity : `pool-gpu`
         - Tolerations : `None`
      - Miscellaneous Settings : `Enable Shared Memory`
   - `Launch` 클릭
3. Notebook 생성 확인

## 2. 각 노트북에 .ipynb 파일 업로드
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. speed.ipynb 파일 다운로드
   #### **Lab5-2-5**
   ```bash
   wget https://github.com/kakaocloud-edu/tutorial/raw/main/Kubeflow/src/ipynb/speed.ipynb
   ```
   - speed.ipynb 파일 생성 확인

4. Notebooks 탭 > `gpu-notebook`의 `CONNECT` 클릭
   - **Note** : `cpu-notebook`, `gpu-notebook` 서로 다름 유의
5. Other 중 `Terminal` 클릭
6. speed.ipynb 파일 다운로드
    #### **Lab5-2-10**
   ```bash
    wget https://github.com/kakaocloud-edu/tutorial/raw/main/Kubeflow/src/ipynb/speed.ipynb
   ```
   - speed.ipynb 파일 생성 확인

## 3. 노트북 속도 비교
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭\
   Notebooks 탭 > `gpu-notebook`의 `CONNECT` 클릭
2. cpu-notebook의 speed.ipynb 파일 `RUN` 클릭
   - 진행 상황 확인
3. gpu-notebook의 speed.ipynb 파일 `RUN` 클릭
   **Note**: 위의 cpu-notebook 실습과 동일
   - 진행 상황 확인
4. 결과 값 비교
   - Training time이 서로 다른 것을 확인
## 4. Kubeflow Tensorboard (약 3분 소요)
1. Notebooks 탭 > `gpu-notebook`의 `CONNECT` 클릭\
   **Note**: 위 실행에 의하여 log(logs/fit/) 날짜별로 생성됨을 확인
2. Tensorboards 탭 > `+ New TensorBoard` 클릭
3. Tensorboard 설정 정보 작성
   - 이름 : `tensorboard`
   - `PVC` 클릭
   - PVC name : `gpu-notebook-volume`
   - Mount Path : `logs/fit/`
   - `CREATE` 클릭
4. 생성된 TensorBoard의 `CONNECT` 클릭
5. 생성된 Tensorboards 목록 확인
   - Scalars (스칼라)
      - 정확도 (Accuracy)와 손실 (Loss) 값 체크
      - TensorBoard 콜백을 설정하면, 모델 학습 시 각 에포크마다 loss와 accuracy 같은 지표가 자동으로 로그에 저장됨
   - Graphs (그래프)
      - 모델 그래프 시각화 (Model Graph Visualization)
   - Distributions (분포)
      - 가중치 및 편향 분포 (Weights and Biases Distribution)
   - Histogram (히스토그램)
      - 가중치 및 편향 히스토그램 (Weights and Biases Histograms)
