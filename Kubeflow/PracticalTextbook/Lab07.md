# Training Operator를 활용한 병렬 학습
Training Operator를 사용하여 병렬 학습 환경을 구축하고 PyTorchJob을 통해 FashionMNIST 데이터를 학습하는 과정을 이해하는 실습입니다.

## 1. pytorch용 CPU 기반 노트북 생성
1.  `Notebooks` 탭  클릭 
2. `+ New Notebook` 클릭
    - 노트북 설정 정보
        - Name
            - Name: `train-test`
            - Namespace: `본인 네임스페이스` (드롭다운에 본인 계정 것만 뜨므로 그대로 선택)
        - Docker Image
            - Image: `kc-kubeflow-registry/jupyter-pyspark-pytorch:v1.10.0.py311.1a`
        - CPU/RAM
            - Requested CPUs: `2`
            - Requested memory in Gi: `6`
        - GPUs
            - Number of GPUs: `None`
        - Workspace Valume, Data Valumes, Configurations : `모두 기본값 사용`
        - Affiinity/Tolerations
    
            - Affiinity : `pool-worker 선택`
            - Tolerations: `None`
        - Miscellaneous Settings : Enable Shared Memory
    - `LAUNCH` 클릭
4. `train-test` > `CONNECT` 버튼 클릭
5. Other 중 `Terminal` 클릭
6. 실습을 위해 터미널에 아래 명령어를 입력하여 `fashionmnist_pytorch_parallel_train_with_tj.ipynb` 파일 다운
    #### **lab7-1-6**
    ```bash
    wget -O fashionmnist_pytorch_parallel_train_with_tj.ipynb "https://objectstorage.kr-central-2.kakaocloud.com/v1/32ac749f528f41958493b28d9387911c/kubeflow/fashionmnist_pytorch_parallel_train_with_tj_cpu.ipynb"
    ```
    - `fashionmnist_pytorch_parallel_train_with_tj.ipynb` 파일 생성 확인
    - **Note**: CPU 전용으로 수정된 버전입니다 (`nccl`→`gloo`, `cuda`→`cpu`, `MAX_EPOCHS` 100→3, GPU 리소스 요청 제거)

## 2. 모델 학습 코드 살펴보기 
1. 우측 화면 영역에 실습 내용 확인
    - `class NeuralNetwork`
    - `load_train_dataset_model_and_opt()`
    
## 3. 노트북 코드 결과 확인 
1. `TrainingClient`를 사용하여 트레이닝 Job을 생성
2. `get_job_pod_names`를 통해 pod 목록 확인
3. `get_job_logs`를 통해 특정 pod의 로그 확인
4. `delete_pytorchjob`를 통해 pytorchjob 삭제
   - **Note**: Traing Job을 삭제하면 뒷 부분 실습이 진행이 안되기 때문에 ‘K8s 내부 동작 확인’ 실습 후 삭제 진행합니다

## 4. K8s 내부 동작 확인
   - **Note**: 아래 명령어는 노트북 셀에 `!`를 붙여서 입력합니다(터미널이 아닌 노트북 코드 셀). `-n` 뒤 네임스페이스는 본인 것으로 바꿔서 입력하세요 — 예시로 쓰인 `kbm-u-kubeflow-tutorial`은 다른 계정 네임스페이스라 그대로 치면 권한(Forbidden) 에러가 납니다. 본인 네임스페이스는 노트북 셀에 아래처럼 입력하면 확인 가능합니다.
   ```bash
   !kubectl config view --minify -o jsonpath='{..namespace}'
   ```
1. 앞에서 쓰던 노트북 하단(코드 셀)에 명령어 입력해서 PytorchJob 내용 확인
    #### **lab7-4-1**
    ```bash
    !kubectl get pytorchjobs -n <본인 네임스페이스> -o yaml
    ```
    - `pytorchReplicaSpecs` 하위에 각각 `Master` 1개, `Worker` 4개 확인
        - `containers` 필드에 수행 학습 코드 확인 가능 (args 필드)

2. 본인 네임스페이스에서 `parallel-train-pytorch-`로 시작하는 모든 파드를 확인
    #### **lab7-4-2**
    ```bash
    !kubectl get po -n <본인 네임스페이스> | grep parallel-train-pytorch-
    ```

3. delete_pytorchjob 를 통해 pytorchjob 삭제
    - 실행 결과 확인
