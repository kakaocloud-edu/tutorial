
# kubernetes Engine 클러스터에 웹서버 수동 배포 실습

Spring application 배포를 위한 Service, Ingress, ConfigMap, Job의 yaml 파일들을 다운 받아 배포하고, 배포된 프로젝트를 브라우저로 확인하는 실습입니다.


## 1. YAML 파일 다운 및 설정
1. 생성해 놓은 yaml 디렉터리 이동
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab6-1-1**
   ```bash
   cd yaml
   ```
   ```bash
   ls -al
   ```
   
2. lab6-manifests.yaml 확인
   #### **lab6-2-1**
   ```bash
   less lab6-manifests.yaml
   ```

3. 레지스트리 인증을 위한 시크릿키 생성
   #### **lab6-8-1**
   ```bash
   kubectl create secret docker-registry regcred \
   --docker-server=${PROJECT_NAME}.kr-central-2.kcr.dev \
   --docker-username=${ACC_KEY} \
   --docker-password=${SEC_KEY} \
   --docker-email=${EMAIL_ADDRESS}
   ```

## 2. YAML 파일 배포
1. 리소스 초기화
   #### **lab6-2-1**
   ```
   kubectl delete -A ValidatingWebhookConfiguration ingress-nginx-admission
   ```

2. YAML 파일 배포
   #### **lab6-2-2-1**
   ```
   kubectl apply -f ./lab6-manifests.yaml
   ```

3. 배포한 내용 확인
   #### **lab6-2-3-1**
   ```
   kubectl get all -o wide
   ```
   
4. 배포한 내용 확인(Configmap, Secret)
   #### **lab6-2-4-1**
   ```
   kubectl get configmap
   ```

   #### **lab6-2-4-2**
   ```
   kubectl get secret
   ```

## 3.배포한 프로젝트 웹에서 확인

 1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > Load Balancer
 2. 두 개의 Load Balancer의 Public IP를 복사
 3. 브라우저 주소창에 복사한 IP 주소 각각 입력
    - 배포한 프로젝트 구동 확인
