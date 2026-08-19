# Gateway API 컨트롤러 배포 실습

Gateway API 표준 리소스와 NGINX Gateway Fabric을 배포하고, Gateway를 통해 AZ별 Load Balancer가 생성되는 과정을 확인하는 실습입니다.

## 실습 구성과 연결 흐름

이 실습과 다음 Lab에서 배포하는 주요 자원과 역할은 다음과 같습니다.

1. **Gateway API 표준 CRD**
   - Kubernetes가 `GatewayClass`, `Gateway`, `HTTPRoute` 같은 Gateway API 리소스를 이해할 수 있도록 API 스키마를 추가합니다.
2. **NGINX Gateway Fabric 컨트롤러**
   - Gateway API 리소스의 상태를 감시하고, 선언한 설정이 실제 NGINX 프록시와 Load Balancer에 반영되도록 관리합니다.
3. **GatewayClass `nginx`**
   - 어떤 컨트롤러가 Gateway를 담당할지 지정하는 클러스터 범위 리소스입니다. NGINX Gateway Fabric 설치 시 생성됩니다.
4. **Gateway `kc-gateway`**
   - 외부 요청을 받을 HTTP 80번 포트와 Route 연결 범위를 정의합니다. 이 Gateway를 생성하면 NGINX 데이터 플레인 파드와 LoadBalancer 타입 Service가 만들어집니다.
5. **HTTPRoute**
   - 다음 Lab에서 배포하며, Gateway로 들어온 요청을 애플리케이션 Service로 전달하는 규칙을 정의합니다.

모든 자원이 배포되면 요청은 다음 순서로 전달됩니다.

```text
사용자 → Public IP → 카카오클라우드 Load Balancer → Gateway Service
      → NGINX 데이터 플레인 파드 → HTTPRoute → 애플리케이션 Service → 애플리케이션 Pod
```

이번 Lab이 끝나면 Gateway가 외부 요청을 받을 준비가 완료됩니다. 아직 HTTPRoute를 배포하지 않았으므로 Public IP 접속 시 `404 Not Found`가 표시될 수 있으며, 다음 Lab에서 HTTPRoute와 애플리케이션을 배포하면 웹 페이지가 표시됩니다.

## 1. Gateway API 표준 CRD 배포

1. 노드의 가용 영역 확인 및 Helm 설치
   - 첫 번째 명령은 워커 노드 목록에 가용 영역 레이블을 함께 표시합니다. `ZONE` 열에서 `kr-central-2-a`, `kr-central-2-b`에 Ready 노드가 각각 존재하는지 확인합니다.
   - 두 번째 명령은 Helm이 이미 설치되어 있는지 확인하고, 없을 때만 공식 설치 스크립트로 Helm을 설치합니다. Helm은 NGINX Gateway Fabric을 패키지 단위로 설치하고 관리하는 도구입니다.
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력

   #### **lab5-1-1**
   ```bash
   kubectl get nodes -L topology.kubernetes.io/zone
   command -v helm >/dev/null || curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | sudo bash
   ```

2. Gateway API 표준 CRD 배포
   - 이 명령은 Kubernetes가 `Gateway`, `HTTPRoute` 같은 Gateway API 리소스를 이해할 수 있도록 **CRD(CustomResourceDefinition)**를 설치하는 단계입니다.
   - `kubectl kustomize`가 NGINX Gateway Fabric 2.3.0과 호환되는 표준 CRD 묶음을 렌더링하고, 파이프(`|`) 뒤의 `kubectl apply -f -`가 렌더링된 내용을 클러스터에 적용합니다.

   #### **lab5-1-2**
   ```bash
   kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.3.0" | kubectl apply -f -
   ```

3. 생성된 Gateway API CRD 확인
   - 다음 명령은 방금 설치한 6개의 표준 CRD가 실제로 생성되었는지 확인합니다.
   - 이어지는 명령은 해당 CRD를 통해 사용할 수 있게 된 Gateway API 리소스의 종류와 API 버전을 보여 줍니다.

   #### **lab5-1-3**
   ```bash
   kubectl get crd \
     backendtlspolicies.gateway.networking.k8s.io \
     gatewayclasses.gateway.networking.k8s.io \
     gateways.gateway.networking.k8s.io \
     grpcroutes.gateway.networking.k8s.io \
     httproutes.gateway.networking.k8s.io \
     referencegrants.gateway.networking.k8s.io

   kubectl api-resources --api-group=gateway.networking.k8s.io
   ```
   - 모든 CRD의 `STATUS` 또는 생성 결과가 정상이고, `gatewayclasses`, `gateways`, `httproutes` 등이 출력되는지 확인합니다.

## 2. NGINX Gateway Fabric 배포

NGINX Gateway Fabric은 Kubernetes Gateway API를 실제로 구현하는 컨트롤러입니다. 사용자가 `Gateway`와 `HTTPRoute`를 선언하면 이를 감시하여 NGINX 데이터 플레인의 설정을 만들고 지속적으로 원하는 상태를 유지합니다.

1. Helm을 이용해 NGINX Gateway Fabric 배포
   - `helm install ngf`는 `ngf`라는 이름으로 Helm 릴리스를 생성합니다.
   - `oci://ghcr.io/nginx/charts/nginx-gateway-fabric`은 NGINX 공식 OCI Helm Chart 주소이며, `--version 2.3.0`으로 실습에서 검증한 버전을 고정합니다.
   - `--namespace nginx-gateway --create-namespace`는 전용 네임스페이스를 생성하여 컨트롤러 자원을 분리합니다.
   - `nginx.kind=daemonSet`은 Gateway의 NGINX 데이터 플레인 파드를 각 워커 노드에 하나씩 배포합니다.
   - `externalTrafficPolicy=Local`은 Load Balancer가 요청을 받은 노드의 로컬 Gateway 파드로 전달하도록 하여 클라이언트 원본 IP를 보존하고 AZ별 상태 확인이 가능하도록 합니다.

   #### **lab5-2-1**
   ```bash
   helm install ngf oci://ghcr.io/nginx/charts/nginx-gateway-fabric \
     --version 2.3.0 \
     --namespace nginx-gateway \
     --create-namespace \
     --set nginx.kind=daemonSet \
     --set nginx.service.externalTrafficPolicy=Local
   ```

2. NGINX Gateway Fabric이 만든 자원 확인
   - 첫 번째 명령은 컨트롤러 Deployment와 Pod, 컨트롤러가 사용하는 ServiceAccount를 확인합니다.
   - 두 번째 명령은 `GatewayClass nginx`가 생성되었는지 확인합니다.
   - 세 번째 명령은 NGINX Gateway Fabric이 내부 설정에 사용하는 전용 CRD를 확인합니다.

   #### **lab5-2-2**
   ```bash
   kubectl get deployment,pod,serviceaccount -n nginx-gateway
   kubectl get gatewayclass nginx
   kubectl get crd | grep gateway.nginx.org
   ```

3. 컨트롤러 및 GatewayClass 준비 상태 확인
   - `kubectl rollout status`는 컨트롤러 Deployment의 새 Pod가 정상 실행될 때까지 기다립니다.
   - `kubectl wait`는 컨트롤러가 `GatewayClass nginx`를 자신이 관리할 대상으로 승인하여 `Accepted=True`가 될 때까지 기다립니다.

   #### **lab5-2-3**
   ```bash
   kubectl rollout status deployment/ngf-nginx-gateway-fabric -n nginx-gateway --timeout=5m
   kubectl wait gatewayclass/nginx --for=condition=Accepted --timeout=2m
   ```

## 3. Gateway 및 LoadBalancer 배포

1. <a href="../src/manifests/gateway.yaml" target="_blank">Gateway</a> 배포
   - 이 명령은 `nginx-gateway` 네임스페이스에 `kc-gateway`를 생성합니다. Gateway는 `GatewayClass nginx`를 사용하고 HTTP 80번 포트에서 요청을 받습니다.
   - `allowedRoutes.namespaces.from: All` 설정으로 다음 Lab의 `default` 네임스페이스에 생성할 HTTPRoute가 이 Gateway에 연결될 수 있습니다. 운영 환경에서는 조직의 네임스페이스 정책에 맞게 범위를 제한합니다.

   #### **lab5-3-1**
   ```bash
   kubectl apply -f /home/ubuntu/tutorial/AdvancedCourse/src/manifests/gateway.yaml
   ```

2. Gateway가 만든 자원과 준비 상태 확인
   - Gateway를 생성하면 NGINX Gateway Fabric이 `kc-gateway-nginx` DaemonSet과 LoadBalancer 타입 Service를 자동으로 만듭니다.
   - 첫 번째 명령은 Gateway 구성이 데이터 플레인에 반영되어 `Programmed=True`가 될 때까지 기다립니다.
   - 두 번째 명령은 각 워커 노드의 Gateway 파드가 준비될 때까지 기다립니다.
   - 나머지 명령은 네임스페이스의 전체 워크로드와 Gateway 상태를 확인합니다.

   #### **lab5-3-2**
   ```bash
   kubectl wait gateway/kc-gateway -n nginx-gateway --for=condition=Programmed --timeout=5m
   kubectl rollout status daemonset/kc-gateway-nginx -n nginx-gateway --timeout=5m
   kubectl get all -n nginx-gateway
   kubectl get gatewayclass nginx
   kubectl get gateway kc-gateway -n nginx-gateway
   ```
   - `GatewayClass`의 `ACCEPTED`와 `Gateway`의 `PROGRAMMED`가 모두 `True`인지 확인합니다.

3. Gateway Service의 트래픽 정책과 상태 확인 포트 확인
   - 이 명령은 자동 생성된 Service의 타입, 외부 트래픽 정책, Load Balancer 상태 확인용 NodePort를 필요한 열만 선택해 보여 줍니다.

   #### **lab5-3-3**
   ```bash
   kubectl get service kc-gateway-nginx -n nginx-gateway \
     -o custom-columns=NAME:.metadata.name,TYPE:.spec.type,TRAFFIC-POLICY:.spec.externalTrafficPolicy,HEALTH-CHECK-PORT:.spec.healthCheckNodePort
   ```
   - `TYPE`은 `LoadBalancer`, `TRAFFIC-POLICY`는 `Local`인지 확인합니다.

4. Gateway 주소와 DNS 정보 확인
   - 첫 번째 명령의 `--watch` 옵션은 Gateway의 `ADDRESS`가 할당되는 과정을 실시간으로 보여 줍니다. 주소가 표시되면 `Ctrl+C`를 입력합니다.

   #### **lab5-3-4**
   ```bash
   kubectl get gateway kc-gateway -n nginx-gateway --watch
   ```

   - 다음 명령은 Gateway 주소를 변수에 저장하고, 공용 DNS 서버에서 해당 주소가 조회될 때까지 10초 간격으로 확인합니다. Load Balancer 생성 직후에는 DNS 정보 반영에 시간이 걸릴 수 있습니다.

   ```bash
   GATEWAY_ADDRESS=$(kubectl get gateway kc-gateway -n nginx-gateway -o jsonpath='{.status.addresses[0].value}')
   until nslookup ${GATEWAY_ADDRESS} 8.8.8.8; do
     echo "DNS 정보가 반영되기를 기다리는 중입니다."
     sleep 10
   done
   ```

## 4. 카카오클라우드 Load Balancer 확인

1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > 로드 밸런서
2. Load Balancer 콘솔창에서 AZ별로 생성된 Load Balancer 확인
3. 생성된 두 개의 Load Balancer 우측 메뉴바 > Public IP 연결 클릭
   - `새로운 Public IP를 생성하고 자동으로 할당` 선택
4. 생성된 두 개의 Load Balancer의 Public IP를 복사
5. 브라우저 주소창에 복사한 IP 주소를 각각 입력
   - HTTPRoute 배포 전에는 NGINX의 `404 Not Found`가 표시될 수 있습니다.

> Load Balancer 대상이 `Unhealthy`라면 콘솔의 상태 확인 포트와 **lab5-3-3**에서 확인한 `HEALTH-CHECK-PORT`가 같은지 확인합니다.
