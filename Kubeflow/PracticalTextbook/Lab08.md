# Training Operator를 활용한 병렬 학습
Training Operator를 사용하여 병렬 학습 환경을 구축하고 PyTorchJob을 통해 FashionMNIST 데이터를 학습하는 과정을 이해하는 실습입니다.

## 1. 노트북 생성
1.  `Notebooks` 탭  클릭 
2. `+ New Notebook` 클릭
3. Notebook 이름, 네임스페이스, 이미지 설정
    - `Name`: train-test
    - `Namespace`: kbm-u-Kubeflow-tutorial
    - `Image`: mlops-pipelines/jupyter-pyspark-pytorch:v1.0.1.py36
4. CPU / RAM / GPUs 설정
    - `Requested CPUs`: 2
    - `Requested memory in Gi`: 6
5. Volume / Configurations 설정
    - 모두 `기존 값` 사용
6. Affiinity / Tolerations 설정
    - `Affiinity`: pool-worker 선택
    - `Tolerations`: None(기존 값) 사용
    - `Miscellaneous Settings`: 기존 값 사용
    - `LAUNCH` 클릭
7. `train-test` > `CONNECT` 버튼 클릭
8. Notebook에서 `Terminal` 선택
9. 실습을 위한 `fashionmnist_pytorch_parallel_train_with_tj.ipynb` 파일 다운
    - 터미널에 아래 명령어를 입력하세요.
     #### **lab8-1-9**
   ```bash
   wget -O fashionmnist_pytorch_parallel_train_with_tj.ipynb "https://objectstorage.kr-central-1.kakaoi.io/v1/c745e6650f0341a68bb73fa222e88e9b/kbm-files/guide_docs%2Fhands_on%2Ffashion-mnist-parallel-train%2Ffashionmnist_pytorch_parallel_train_with_tj.ipynb"
   ```
    - `fashionmnist_pytorch_parallel_train_with_tj.ipynb` 파일 생성 확인

## 2. 모델 학습 코드 살펴보기 
1. 우측 화면 영역에 실습 내용을 확인
    - `class NeuralNetwork`
    - `load_train_dataset_model_and_opt()`
    
## 3. 노트북 코드 결과 확인 
1. `TrainingClient`를 사용하여 트레이닝 Job을 생성
2. `get_job_pod_names`를 통해 pod들 목록 확인
3. `get_job_logs`를 통해 특정 pod의 로그 확인
4. `delete_pytorchjob`를 통해 pytorchjob 삭제

## 4. k8s 내부 동작 확인
1. PytorchJob 내용 확인
    - 터미널에 아래 명령어를 입력하세요.
     #### **lab8-1-9**
   ```bash
   !kubectl get pytorchjobs -n kbm-u-Kubeflow-tutorial -o yaml
   ```
        - `pytorchReplicaSpecs` 하위에 각각 `Master` 1개, `Worker` 4개 확인
            - `containers` 필드에 수행 학습 코드 확인 가능 (args 필드)

2. Kubernetes 네임스페이스 `kbm-u-Kubeflow-tutorial에서 parallel-train-pytorch-`로 시작하는 모든 파드를 확인
    - 터미널에 아래 명령어를 입력하세요.
     #### **lab8-4-2**
   ```bash
   !kubectl get po -n kbm-u-Kubeflow-tutorial | grep parallel-train-pytorch-
   ```
        

