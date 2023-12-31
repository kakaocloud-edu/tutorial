# Kubernetes Engine 활용하기 

만들어진 웹을 ConfigMap.yaml 파일을 변경해서 웹의 구조를 변경하고 확인합니다. 또한 Deployment 리소스의 replicas 값 변경하여 Pod의 개수를 확인하는 실습과정을 진행합니다.


## 1. yaml 파일을 이용해 배포된 내용 수정하기

1. Pod들의 상태 변화 확인
   - 새로운 터미널에 아래 명령어를 입력하세요.
   #### **lab7-1-1**
   ```bash
   kubectl get po -w
   ```
   
2. lab7-ConfigMap.yaml 파일 수정
   - 터미널에 아래 명령어를 입력하세요.
   #### **lab7-1-2**
   ```bash
   sudo vi lab6-ConfigMap.yaml
   ```

3. `WelCome_MESSAGE` 내용을 변경해 웹 사이트 문구 변경하기

   **Note** 아래와 같은 방식으로 문구를 변경하면 됩니다.
   #### **lab7-1-3**
   ```bash
   apiVersion: v1
   kind: ConfigMap
   metadata:
      name: app-config
   data:
      WELCOME_MESSAGE: "ConfigMap변경 실습"
      BACKGROUND_COLOR: "#4a69bd"
   ```
## 2. yaml 파일 배포

1. 수정된 yaml 파일 적용
   #### **lab7-2-1**
   ```bash
   kubectl apply -f ./lab6-ConfigMap.yaml
   ```

2. Pod최신화를 위해 기존 리소스(Pod)제거
   #### **lab7-2-2**
   ```bash
   kubectl delete pod —all
   ```
## 3. 변경된 내용 웹에서 확인

1. 웹 사이트에 재접속해서 변경한 문구가 적용되었는지 확인하기

## 4. Deployment 리소스의 replicas 값 변경

1. Pod들의 상태 변화 확인
   - 새로운 터미널에 아래 명령어를 입력하세요.
   #### **lab7-4-1**
   ```bash
   kubectl get po -w
   ```
2. Pod 확인
   #### **lab7-4-2**
   ```bash
   kubectl get pod
   ```
3. Replicas 수 3개로 늘리기
   #### **lab7-4-3**
   ```bash
   kubectl scale deployment demo-deployment –replicas=3
   ```
4. Pod 확인
   #### **lab7-4-4**
   ```bash
   kubectl get pod
   ```
5. Replicas 수 2개로 줄이기
   #### **lab7-4-5**
   ```bash
   kubectl scale deployment demo-deployment –replicas=2
   ```
5. Pod 확인
   #### **lab7-4-5**
   ```bash
   kubectl get pod
   ```
