# Kubernetes Engine 활용하기 

만들어진 웹을 ConfigMap.yaml 파일을 변경해서 웹의 구조를 변경하고 확인합니다. 또한 Deployment 리소스의 replicas 값 변경하여 Pod의 개수를 확인하는 실습과정을 진행합니다.

## 1. Deployment 리소스의 replicas 값 변경

1. Pod들의 상태 변화 확인
   - 새로운 터미널에 아래 명령어를 입력하세요.
    #### **lab7-1-1-1**
   ```bash
   cd {keypair.pem 다운로드 위치}
   ```
   #### **lab7-1-1-2**
   ```bash
   ssh -i keyPair.pem centos@{bastion의 public ip주소}
   ```
   - **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.
  
   #### **lab7-1-1-3**
   ```bash
   kubectl get po -w
   ```
   
2. Replicas 수 3개로 늘리기
   #### **lab7-1-2**
   ```bash
   kubectl scale deployment demo-deployment --replicas=3
   ```
3. Pod들의 상태 변화 확인
4. 변경된 첫 번째 웹 사이트 확인
5. 변경된 두 번째 웹 사이트 확인
6. 변경된 세 번째 웹 사이트 확인
7. Replicas 수 2개로 줄이기
   #### **lab7-1-7**
   ```bash
   kubectl scale deployment demo-deployment --replicas=2
   ```
8. Pod들의 상태 변화 확인

9. 변경된 첫 번째 웹 사이트 확인
10. 변경된 두 번째 웹 사이트 확인
   
## 2. yaml 파일을 이용해 배포된 내용 수정하기

   
1. lab6-ConfigMap.yaml 파일 수정
   - 터미널에 아래 명령어를 입력하세요.
   #### **lab7-2-1**
   ```bash
   sudo vi lab6-ConfigMap.yaml
   ```
2.  Google에 color picker 검색 후 원하는 색상 HEX값 복사

     
3. ConfigMap.yaml 파일 내용 변경후 저장

   #### **lab7-2-3**
   
   **Note** 아래와 같은 방식으로 문구를 변경하면 됩니다.   
   ```bash
   apiVersion: v1
   kind: ConfigMap
   metadata:
      name: app-config
   data:
      WELCOME_MESSAGE: "ConfigMap변경 실습"
      BACKGROUND_COLOR: "{HEX값}"
   ```
   
## 3. yaml 파일 배포

1. 수정된 yaml 파일 적용
   #### **lab7-3-1**
   ```bash
   kubectl apply -f ./lab6-ConfigMap.yaml
   ```
   

2. 실행 중인 Deployment를 재시작
   #### **lab7-3-2**
   ```bash
   kubectl rollout restart deployment demo-deployment
   ```
3. Pod들의 상태 변화 확인

## 4. 변경된 내용 웹에서 확인

1. 변경 된 첫 번째 웹사이트 확인
2. 변경 된 두 번째 웹사이트 확인
