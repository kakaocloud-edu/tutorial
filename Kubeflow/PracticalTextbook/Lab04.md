# Kubeflow의 쿠버네티스 리소스 확인해보기
쿠버네티스 위에서 동작하는 Kubeflow의 리소스들이 어떤 것들이 있는지 확인해 보는 실습입니다.

## 1. 네임스페이스 확인 

1. Kubeflow를 위한 네임스페이스들 확인
   - **Note**: 터미널에서 명령어 입력
   #### **Lab4-1-1**
   ```bash
   kubectl get ns
   ```
   ![image](https://github.com/KOlizer/tutorial/assets/127844467/c8476ac8-462d-4379-9d06-fa315811398a)


## 2. CPU 기반 Jupyter Notebook 생성

1. kbm-u-Kubeflow-tutorial 네임스페이스 선택 > 좌측 메뉴바의 `Notebooks` 탭 클릭 
2. `+ New Notebook` 클릭
   - 노브북 설정
     - Name : `cpu-notebook`
     - Namespace : `kbm-u-Kubeflow-tutorial`
     - Image : `mlops-pipelines/jupyter-pytorch-full:v1.0.1.py36`
     - Requested CPUs : `2`
     - Requested memory in Gi : `8`
     - Volume / Configurations 설정 : `모두 기존 값 사용`
     - Affiinity : `pool-worker` 
     - Tolerations : `None(기존 값)` 
     - Miscellaneous Settings :  `기존 값 사용`
3. `LAUNCH` 클릭
4. Notebook 생성 확인


## 3. 특정 네임스페이스의 리소스 확인

1. Kubeflow 네임스페이스의 리소스 출력
   - 위에서 생성한 Notebook에 명령어 입력
   - **Note**: Other 중 `Python` 클릭
   #### **lab4-3-1**
     ```bash
     !kubectl get all
     ```

2. Kubernetes StatefulSet 리소스를 YAML 형식으로 출력
   #### **lab4-3-2**
     ```bash
     !kubectl get sts -o yaml
     ```

## 4. Service Accounts 목록 조회

1. Kubernetes ServiceAccount 리소스를 조회하는 명령어 입력
   #### **lab4-4-1**
     ```bash
     !kubectl get sa
     ```
2. 매핑된 바인딩 확인
   - kbm-u-Kubeflow-tutorial 네임스페이스의 모든 RoleBinding 목록 조회
   - **Note**: 터미널 창에서 입력
   #### **lab4-4-2**
     ```bash
     kubectl get rolebinding -n kbm-u-Kubeflow-tutorial
     ```

   - kbm-u-Kubeflow-tutorial 네임스페이스의 default-editor RoleBinding의 세부 정보를 YAML 형식으로 조회
   #### **lab4-4-3**
     ```bash
     kubectl get rolebinding default-editor -n kbm-u-Kubeflow-tutorial -o yaml

     ```

## 5. PVC 리소스 조회
1. 현재 Namespace에서 모든 PersistentVolumeClaim(PVC) 리소스 조회
   - **Note**: 위에서 생성한 Notebook에서 입력
   #### **lab4-5-1**
     ```bash
     !kubectl get pvc
     ```
