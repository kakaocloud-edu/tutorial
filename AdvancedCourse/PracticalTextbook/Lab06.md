# kubernetes engine 클러스터에 웹서버 수동 배포 실습

Spring application 배포를 위한 Service, Ingress, ConfigMap, ConfigMap2의 yaml 파일들을 다운 받아 배포하고, 배포된 프로젝트를 브라우저로 확인하는 실습입니다.


## 1. YAML 파일 다운 및 설정

1. YAML 압축파일 다운 및 확인
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   #### **lab6-1-1-1**
   ```bash
   wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/lab6Yaml.tar
   ```

   #### **lab6-1-1-2**
   ```bash
   ls
   ```

2. YAML 압축파일 압축 풀기
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   #### **lab6-1-2-1**
   ```bash
   tar -xvf lab6Yaml.tar
   ```

   #### **lab6-1-2-2**
   ```bash
   mv ../lab6* .
   ```

   #### **lab6-1-2-3**
   ```bash
   ls
   ```

## 2. YAML 파일 배포


1. 다운 받은 yaml들 배포

   **Note** Yaml 파일 간 의존성 문제로 배포 순서를 지켜주세요.
   #### **lab6-2-2-1**
   ```
   kubectl apply -f ./lab6-ConfigMap.yaml
   ```
   
   #### **lab6-2-2-2**
   ```
   kubectl apply -f ./lab6-ConfigMapDB.yaml
   ```

   #### **lab6-2-2-3**
   ```
   kubectl apply -f ./lab6-Secret.yaml
   ```

   #### **lab6-2-2-4**
   ```
   kubectl apply -f ./lab6-Job.yaml
   ```

   #### **lab6-2-2-5**
   ```
   kubectl apply -f .
   ```

3. 배포한 내용 확인
   #### **lab6-2-3**
   ```
   kubectl get all -o wide
   ```

## 3.배포한 프로젝트 웹에서 확인

 1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > Load Balancer
 2. 두 개의 Load Balancer의 Public IP를 복사
 3. 브라우저 주소창에 복사한 IP 주소 각각 입력
    - 배포한 프로젝트 구동 확인
