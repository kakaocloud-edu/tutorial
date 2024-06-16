# Kubeflow의 쿠버네티스 리소스 확인해보기
쿠버네티스 위에서 동작하는 Kubeflow의 리소스들이 어떤 것들이 있는지 확인해 보는 실습입니다.

## 1. 네임스페이스 확인 (데모)

1. Kubeflow를 위한 네임스페이스들 확인
   - **Note**: 터미널에서 명령어 입력
   #### **Lab4-1-1**
   ```bash
   kubectl get ns
   ```
   ![image](https://github.com/KOlizer/tutorial/assets/127844467/c8476ac8-462d-4379-9d06-fa315811398a)


## 2. CPU 기반 Jupyter Notebook 생성
   - **Note** : Kubeflow 콘솔에서 진행하는 실습입니다.

1. kbm-u-kubeflow-tutorial 네임스페이스 선택 > 좌측 메뉴바의 `Notebooks` 탭 클릭 
2. `+ New Notebook` 클릭
   - 노트북 설정 정보
      - Name
         - Name : `cpu-notebook`
         - Namespace : `kbm-u-kubeflow-tutorial`
      - Docker Image
         - Image : `mlops-pipelines/jupyter-tensorflow-cuda-full:v1.0.1.py36`
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


## 3. 특정 네임스페이스의 리소스 확인

1. 생성한 `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 Terminal 클릭
3. 특정 네임스페이스의 리소스 확인
   - Kubeflow 네임스페이스의 리소스 출력
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력
   #### **lab4-3-1**
   ```bash
   kubectl get all
   ```

   - Kubernetes StatefulSet 리소스를 YAML 형식으로 출력
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력
   #### **lab4-3-2**
   ```bash
   kubectl get sts -o yaml
   ```

## 4. Service Accounts 목록 조회

1. Kubernetes ServiceAccount 리소스 조회
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력
   #### **lab4-4-1**
   ```bash
   kubectl get sa
   ```
3. 매핑된 바인딩 확인
   - kbm-u-kubeflow-tutorial 네임스페이스의 모든 RoleBinding 목록 조회
   - **Note**: 터미널 창에서 입력
   #### **lab4-4-2-1**
   ```bash
   kubectl get rolebinding -n kbm-u-kubeflow-tutorial
   ```

4. 특정 RoleBinding의 상세 정보 출력
   - kbm-u-kubeflow-tutorial 네임스페이스의 default-editor RoleBinding의 세부 정보를 YAML 형식으로 조회
   - **Note**: 터미널 창에서 입력
   #### **lab4-4-2-2**
   ```bash
   kubectl get rolebinding default-editor -n kbm-u-kubeflow-tutorial -o yaml
   ```

## 5. PVC 리소스 조회
   - 현재 Namespace에서 모든 PersistentVolumeClaim(PVC) 리소스 조회
   - **Note**: 위에서 생성한 Notebook(`cpu-notebook`)에서 입력
   #### **lab4-5-1**
   ```bash
   kubectl get pvc
   ```
