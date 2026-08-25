# 간단한 Notebook 실습
   - **Note** : Kubeflow 콘솔에서 진행하는 실습입니다.
   - **Note** : 원본 실습은 CPU/GPU 노트북 속도를 비교하는 구성이었으나, GPU 리소스 없이 진행할 수 있도록 CPU 노트북(cpu-notebook) 단일 구성으로 변경했습니다.

CPU Notebook에서 Tensorboard, 하이퍼파라미터 튜닝 등을 실습합니다.

## 1. 노트북에 .ipynb 파일 업로드
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. speed_check.ipynb 파일 다운로드
   #### **Lab5-1-3**
   ```bash
   wget -O speed_check.ipynb "https://objectstorage.kr-central-2.kakaocloud.com/v1/32ac749f528f41958493b28d9387911c/kubeflow/speed_check_cpu.ipynb"
   ```
   - speed_check.ipynb 파일 생성 확인

## 2. 노트북 실행
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. cpu-notebook의 speed_check.ipynb 파일 `RUN` 클릭
   - **Note**: 첫 실행 시 tensorflow/CIFAR-10 데이터가 준비돼있지 않으면 자동으로 설치·다운로드(사내 Object Storage 기준)를 진행한 뒤 학습을 시작합니다.
   - 진행 상황 확인
3. 결과 값 확인
   - Training time 및 Test accuracy 확인

## 3. Kubeflow Tensorboard (약 3분 소요)
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭\
   **Note**: 위 실행에 의하여 log(logs/fit/) 날짜별로 생성됨을 확인
2. Tensorboards 탭 > `+ New TensorBoard` 클릭
3. Tensorboard 설정 정보 작성
   - 이름 : `tensorboard`
   - Storage Type : `PVC` 클릭
   - PVC name : `cpu-notebook-volume`
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
