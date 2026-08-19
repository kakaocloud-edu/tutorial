# Kubernetes Engine 클러스터에 웹서버 수동 배포 실습

Spring application 실행에 필요한 ConfigMap, Secret, Job, Service, Deployment를 배포하고, HTTPRoute를 통해 Gateway와 애플리케이션을 연결한 뒤 웹에서 확인하는 실습입니다.

`lab6-manifests.yaml`에는 다음 리소스가 포함되어 있습니다.

- `app-config` ConfigMap: 애플리케이션의 화면 문구와 배경색을 저장합니다.
- `app-secret` Secret: 데이터베이스 접속 정보를 저장합니다.
- `sql-script` ConfigMap과 `sql-job` Job: 데이터베이스 초기화 SQL을 한 번 실행합니다.
- `demo-deployment` Deployment: Spring application Pod를 두 개 실행합니다.
- `kc-spring-service` Service: 여러 애플리케이션 Pod에 트래픽을 분산합니다.
- `kc-spring-route` HTTPRoute: Lab05의 `kc-gateway`로 들어온 `/` 경로 요청을 `kc-spring-service`로 전달합니다.

## 1. YAML 파일 확인 및 레지스트리 인증 설정

1. YAML 디렉터리로 이동하고 파일 확인
   - Lab03의 초기화 스크립트가 원본 매니페스트의 환경 변수 자리에 실습 환경의 값을 넣어 `/home/ubuntu/yaml/lab6-manifests.yaml`을 만들었습니다.
   - `cd`는 해당 디렉터리로 이동하고, `ls -al`은 숨김 파일을 포함한 파일 목록과 권한을 보여 줍니다.
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab6-1-1**
   ```bash
   cd /home/ubuntu/yaml
   ls -al
   ```
   - 목록에 `lab6-manifests.yaml`이 있는지 확인합니다.

2. `lab6-manifests.yaml` 내용 확인
   - `cat`은 배포 전에 YAML 전체 내용을 터미널에 출력합니다. 이미지 주소와 데이터베이스 엔드포인트가 본인의 실습 환경 값으로 치환되었는지 확인합니다.

   #### **lab6-1-2**
   ```bash
   cat lab6-manifests.yaml
   ```

3. Container Registry 인증용 Secret 생성
   - 이 명령은 Kubernetes가 비공개 Kakao Cloud Container Registry에서 애플리케이션 이미지를 가져올 때 사용할 `regcred` Secret을 생성합니다.
   - `--docker-server`는 레지스트리 주소, `--docker-username`과 `--docker-password`는 Lab03에서 설정한 액세스 키입니다.

   #### **lab6-1-3**
   ```bash
   kubectl create secret docker-registry regcred \
     --docker-server=${PROJECT_NAME}.kr-central-2.kcr.dev \
     --docker-username=${ACC_KEY} \
     --docker-password=${SEC_KEY}
   ```

4. 생성한 Secret 확인
   - 보안 값 자체는 출력하지 않고 Secret의 이름과 타입만 확인합니다. `TYPE`이 `kubernetes.io/dockerconfigjson`인지 확인합니다.

   #### **lab6-1-4**
   ```bash
   kubectl get secret regcred -o custom-columns=NAME:.metadata.name,TYPE:.type
   ```

## 2. YAML 파일 배포

1. Gateway 준비 상태 확인
   - 첫 번째 명령은 Lab05에서 만든 Gateway의 현재 주소와 상태를 보여 줍니다.
   - 두 번째 명령은 Gateway 구성이 실제 NGINX 데이터 플레인에 반영되어 `Programmed=True`인지 확인합니다.

   #### **lab6-2-1**
   ```bash
   kubectl get gateway kc-gateway -n nginx-gateway
   kubectl wait gateway/kc-gateway -n nginx-gateway --for=condition=Programmed --timeout=2m
   ```

2. YAML 파일 배포
   - `kubectl apply -f`는 YAML에 선언한 2개의 ConfigMap, Secret, Job, HTTPRoute, Service, Deployment를 생성하거나 기존 상태를 선언한 내용으로 갱신합니다.

   #### **lab6-2-2**
   ```bash
   kubectl apply -f ./lab6-manifests.yaml
   ```

3. 애플리케이션과 데이터베이스 초기화 상태 확인
   - `rollout status`는 Deployment의 애플리케이션 Pod가 준비될 때까지 기다립니다.
   - `kubectl wait`는 데이터베이스 초기화 Job이 성공적으로 완료될 때까지 기다립니다.
   - `kubectl get all -o wide`는 Pod가 배치된 노드와 IP를 포함해 주요 워크로드 상태를 보여 줍니다.

   #### **lab6-2-3**
   ```bash
   kubectl rollout status deployment/demo-deployment --timeout=5m
   kubectl wait job/sql-job --for=condition=complete --timeout=5m
   kubectl get all -o wide
   ```
   - Deployment의 `READY`가 `2/2`, Job의 `COMPLETIONS`가 `1/1`인지 확인합니다.

4. ConfigMap과 Secret 확인
   - `kubectl get configmap`은 애플리케이션 설정과 SQL 스크립트가 생성되었는지 확인합니다.
   - `kubectl get secret`은 애플리케이션·레지스트리 인증 Secret이 생성되었는지 확인합니다. Secret 값은 기본 목록에 표시되지 않습니다.

   #### **lab6-2-4**
   ```bash
   kubectl get configmap
   kubectl get secret
   ```

5. HTTPRoute 연결 상태 확인
   - 첫 번째 명령은 HTTPRoute의 기본 상태를 보여 줍니다.
   - 두 번째 명령은 Gateway가 Route를 승인했는지와 Route가 참조하는 Service가 유효한지를 조건별로 출력합니다.

   #### **lab6-2-5**
   ```bash
   kubectl get httproute kc-spring-route
   kubectl get httproute kc-spring-route \
     -o jsonpath='{range .status.parents[*].conditions[*]}{.type}={.status}{"\n"}{end}'
   ```
   - `Accepted=True`는 Gateway가 Route 연결을 허용했다는 뜻입니다.
   - `ResolvedRefs=True`는 `kc-spring-service` 같은 참조 대상이 정상이라는 뜻입니다.

> Pod가 `ImagePullBackOff` 상태라면 Lab04의 이미지 Push 결과와 `regcred`의 액세스 키 권한을 확인합니다. Job이 실패하면 `kubectl logs job/sql-job`으로 데이터베이스 연결 및 SQL 실행 오류를 확인합니다.

## 3. 배포한 프로젝트 웹에서 확인

1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > 로드 밸런서
2. 두 개의 Load Balancer의 Public IP를 복사
3. 브라우저 주소창에 복사한 IP 주소를 각각 입력
   - 두 주소 모두에서 배포한 Spring application 화면이 표시되는지 확인합니다.
   - 화면을 여러 번 새로 고침하여 요청이 서로 다른 애플리케이션 Pod로 분산되는지 확인합니다.
