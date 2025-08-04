# K8s의 내부 동작 확인

쿠버네티스 위에서 동작하는 Kubeflow의 리소스들이 어떤 것들이 있는지 확인해 보는 실습입니다.

## 1. 쿠버네티스에서 kubeflow와 관련된 namespace들을 확인해 보기 (Demo)

1. 터미널에서 Kubeflow를 위한 네임스페이스들 확인
   - **Note**: 터미널에서 명령어 입력
   #### **Lab4-1-1**
   ```bash
   kubectl get ns
   ```

## 2. CPU 기반 Notebook 생성 (약 3분 소요)
   - **Note** : Kubeflow 콘솔에서 진행하는 실습입니다.

1. kbm-u-kubeflow-tutorial 네임스페이스 선택 > 좌측 메뉴바의 `Notebooks` 탭 클릭 
2. `+ New Notebook` 클릭
   - 노트북 설정 정보
      - Name
         - Name : `cpu-notebook`
         - Namespace : `kbm-u-kubeflow-tutorial`
      - Docker Image
         - Image : `mlops-pipelines/jupyter-tensorflow-cuda-full:v1.0.1.py36`
         - **Note**: 이미지 이름 정확하게 확인하기
      - CPU/RAM
         -  Requested CPUs : `2`
         - Requested memory in Gi : `8`
      - GPUs
         - Number of GPUs : `None`
      - Workspace Valume, Data Valumes, Configurations : `모두 기본값 사용`
      - Affiinity/Tolerations
         - Affiinity : `pool-worker` 
         - Tolerations : `None` 
      - Miscellaneous Settings : `Enable Shared Memory`
   - `LAUNCH` 클릭
3. Notebook 생성 확인


## 3. 생성된 Notebook에 접속하여 namespace 내의 리소스들 확인
- 아래 방법 중 3-1이나 3-2로 진행

### 3-1. 각 노트북에 .ipynb 파일 업로드
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. kubectl.ipynb 파일 다운로드
   #### **Lab5-2-5**
   ```bash
   wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/src/ipynb/kubectl.ipynb
   ```
   - kubectl.ipynb 파일 생성 확인 및 더블 클릭 후 내부 코드 실행

### 3-2-1. cpu-notebook과 관련된 k8s 리소스 확인하기
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. 특정 네임스페이스의 리소스 확인
   - Kubeflow 네임스페이스의 리소스 출력
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력
   #### **lab4-3-1**
   ```bash
   kubectl get all
   ```

   - `cpu-notebook`에 대한 Kubernetes StatefulSet 리소스를 YAML 형식으로 출력
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력
   #### **lab4-3-2**
   ```bash
   kubectl get sts cpu-notebook -o yaml
   ```

### 3-2-2. Service Accounts 목록 조회
1. Kubernetes ServiceAccount 리소스 조회 
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력
   #### **lab4-3-3**
   ```bash
   kubectl get sa
   ```
2. 매핑된 바인딩 확인 (데모)
   - kbm-u-kubeflow-tutorial 네임스페이스의 모든 RoleBinding 목록 조회
   - **Note**: 터미널 창에서 입력
   #### **lab4-3-4**
   ```bash
   kubectl get rolebinding -n kbm-u-kubeflow-tutorial
   ```

3. 특정 RoleBinding의 상세 정보 출력 (데모)
   - kbm-u-kubeflow-tutorial 네임스페이스의 default-editor RoleBinding의 세부 정보를 YAML 형식으로 조회
   - **Note**: 터미널 창에서 입력
   #### **lab4-3-5**
   ```bash
   kubectl get rolebinding default-editor -n kbm-u-kubeflow-tutorial -o yaml
   ```

### 3-2-3. PVC 리소스 조회
1. 현재 Namespace에서 모든 PersistentVolumeClaim(PVC) 리소스 조회
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력
   #### **lab4-3-6**
   ```bash
   kubectl get pvc -n kbm-u-kubeflow-tutorial
   ```
