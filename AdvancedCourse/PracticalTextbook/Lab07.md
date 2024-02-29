# Kubernetes Engine 활용하기 

만들어진 웹을 ConfigMap을 변경해서 웹의 구조를 변경하고 확인합니다. 또한 Deployment 리소스의 replicas 값 변경하여 Pod의 개수를 확인하는 실습과정을 진행합니다.

## 1. Deployment 리소스의 replicas 값 변경

1. Pod들의 상태 변화 확인
    #### **lab7-1-1**
   - 새로운 터미널에 아래 명령어를 입력하세요.
   ```bash
   cd {keypair.pem 다운로드 위치}
   ```

   - **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.
   ```bash
   ssh -i keypair.pem ubuntu@{bastion의 public ip주소}
   ```
  
   - 상태 변화 확인을 위해 실시간 변화를 확인 가능한 -w 옵션을 사용한 명령어 입력
   ```bash
   kubectl get po -w
   ```
   
2. Replicas 수 3개로 늘리기
   - 기존 터미널에 아래 명령어를 입력하세요.
   #### **lab7-1-2**
   ```bash
   kubectl scale deployment demo-deployment --replicas=3
   ```
3. 새로운 터미널에서 Pod들의 상태 변화 확인
4. 새로고침을 통해 서버의 호스트 이름이 3가지 Pod 이름으로 바뀌는 것을 확인
5. 변경된 두 번째 웹 사이트 확인
6. 변경된 세 번째 웹 사이트 확인
7. Replicas 수 2개로 줄이기
   #### **lab7-1-7**
   ```bash
   kubectl scale deployment demo-deployment --replicas=2
   ```
8. 새로운 터미널에서 Pod들의 상태 변화 확인

9. 새로고침을 통해 서버의 호스트 이름이 2가지 Pod 이름으로 바뀌는 것을 확인
10. 변경된 두 번째 웹 사이트 확인
   
## 2. yaml 파일을 이용해 배포된 내용 수정해보기

1. yaml 파일이 있는 경로로 이동 및 lab6-manifests.yaml 파일 수정
   #### **lab7-2-1**
   ```bash
   cd yaml
   ```
   ```bash
   sudo vi lab6-manifests.yaml
   ```
3.  Google에 color picker 검색 후 원하는 색상 HEX값 복사
    - [color picker](https://www.google.com/search?client=safari&rls=en&q=color+picker&ie=UTF-8&oe=UTF-8)

4. ConfigMap.yaml 파일 내용 변경후 저장
   
   **Note** 아래와 같은 방식으로 문구를 변경하면 됩니다.   
   ```bash
   apiVersion: v1
   kind: ConfigMap
   metadata:
      name: app-config
   data:
      WELCOME_MESSAGE: "ConfigMap변경 실습"
      BACKGROUND_COLOR: "{HEX값}" #특수문자 처리를 위해 반드시 쌍따옴표로 감싸주세요. ex)"#4287f5"
   ```
   
## 3. yaml 파일 배포

1. 수정된 yaml 파일 적용
   #### **lab7-3-1**
   ```bash
   kubectl apply -f ./lab6-manifests.yaml
   ```
   

2. 수정사항 반영을 위해 실행 중인 Deployment를 재시작
   #### **lab7-3-2**
   ```bash
   kubectl rollout restart deployment demo-deployment
   ```
3. Pod들의 상태 변화 확인

## 4. 변경된 내용 웹에서 확인
1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > Load Balancer
2. 생성된 두 개의 Load Balancer의 Public IP를 복사
3. 브라우저 주소창에 복사한 IP 주소 각각 입력
     - 변경된 내용 확인
