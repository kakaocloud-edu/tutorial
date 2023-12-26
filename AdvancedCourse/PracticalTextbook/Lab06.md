# kubernetes engine 클러스터에 웹서버 수동 배포 실습

Spring application 배포를 위한 Deployment, Service, Ingress, ConfigMap, Secret의 yaml 파일들을 다운 받아 배포하고, 배포된 프로젝트를 웹에서 확인하는 실습입니다.


## 1. YAML 파일 다운 및 설정

1. YAML 압축파일 다운 - 터미널 명령어 입력
    #### **lab6-1-1-1**
    ```bash
    wget https://github.com/NOOJU/test/raw/main/TEST_YAML.tar
    ```
    #### **lab6-1-1-2**
    ```bash
    ls
    ```

2. AML 압축파일 압축 풀기 - 터미널 명령어 입력
    #### **lab6-1-2-1**
    ```bash
    tar -xvf TEST_YAML.tar
    ```
    #### **lab6-1-2-2**
    ```bash
    ls
    ```

3. vi로 프로젝트명 변경하는 내용 추가

## 2. YAML 파일 배포

1. 원활한 실습 진행을 위한 리소스 초기화
   #### **lab6-2-1**
   ```
   kubectl delete -A ValidatingWebhookConfiguration ingress-nginx-admission
   ```

2. 다운 받은 yaml들 배포
   #### **lab6-2-2-1**
   ```
   kubectl apply -f test-deployment.yaml
   ```
   
   #### **lab6-2-2-2**
   ```
   kubectl apply -f test-service.yaml
   ```

   #### **lab6-2-2-3**
   ```
   kubectl apply -f test-ingress.yaml
   ```

   #### **lab6-2-2-4**
   ```
   kubectl apply -f test-configmap.yaml
   ```

   #### **lab6-2-2-5**
   ```
   kubectl apply -f test-secret.yaml
   ```

3. 배포한 내용 확인
   #### **lab6-2-3**
   ```
   kubectl get all -o wide
   ```

## 3.배포한 프로젝트 웹에서 확인

 1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > Load Balancer
 2. 두 번째 Load Balancer의 Public IP를 복사
 3. 브라우저 주소창에 복사한 IP 주소 입력
    - 배포한 프로젝트 구동 확인
