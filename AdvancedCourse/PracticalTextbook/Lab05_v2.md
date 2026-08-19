# Gateway API 컨트롤러 배포 실습

Gateway API 표준 CRD와 NGINX Gateway Fabric을 배포하고 Gateway 파드, 서비스, AZ별로 생성된 Load Balancer를 확인하는 실습입니다.

## 0. v2 실습 파일 준비

1. v2 브랜치로 전환
     - `/home/ubuntu/tutorial`에 변경 중인 파일이 없어야 함
     #### **lab5-v2-0-1**
     ```bash
     sudo git -C /home/ubuntu/tutorial status --short
     sudo git -C /home/ubuntu/tutorial fetch origin
     sudo git -C /home/ubuntu/tutorial switch agent/gateway-api-v2-tutorial
     ```
     - 첫 번째 명령의 출력이 있다면 변경 내용을 확인한 후 브랜치를 전환


## 1. NGINX Gateway Fabric 배포 (Demo)

1. 노드의 가용 영역 확인 및 Helm 설치
     - 접속 중인 Bastion VM 인스턴스에 명령어 입력
     #### **lab5-1-1**
     ```bash
     kubectl get nodes -L topology.kubernetes.io/zone
     command -v helm >/dev/null || curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | sudo bash
     ```
     - `ZONE` 열에서 `kr-central-2-a`, `kr-central-2-b`에 Ready 노드가 각각 존재하는지 확인

2. Gateway API 표준 CRD 배포
     #### **lab5-1-2**
     ```bash
     kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.3.0" | kubectl apply -f -
     ```

3. NGINX Gateway Fabric 배포
     #### **lab5-1-3**
     ```bash
     helm install ngf oci://ghcr.io/nginx/charts/nginx-gateway-fabric \
       --version 2.3.0 \
       --namespace nginx-gateway \
       --create-namespace \
       --set nginx.kind=daemonSet \
       --set nginx.service.externalTrafficPolicy=Local
     ```
     - `DaemonSet`을 사용해 각 워커 노드에 Gateway 파드를 배포

4. 컨트롤러 및 GatewayClass 상태 확인
     #### **lab5-1-4**
     ```bash
     kubectl rollout status deployment/ngf-nginx-gateway-fabric -n nginx-gateway --timeout=5m
     kubectl wait gatewayclass/nginx --for=condition=Accepted --timeout=2m
     ```

## 2. Gateway 파드 및 서비스 상태 확인

1. <a href="../src/manifests/gateway_v2.yaml" target="_blank">Gateway</a> 배포
     #### **lab5-2-1**
     ```bash
     kubectl apply -f /home/ubuntu/tutorial/AdvancedCourse/src/manifests/gateway_v2.yaml
     ```

2. Gateway 자원들의 상태 확인
     - 접속 중인 Bastion VM 인스턴스에 명령어 입력
     #### **lab5-2-2**
     ```bash
     kubectl wait gateway/kc-gateway -n nginx-gateway --for=condition=Programmed --timeout=5m
     kubectl rollout status daemonset/kc-gateway-nginx -n nginx-gateway --timeout=5m
     kubectl get all -n nginx-gateway
     kubectl get gatewayclass nginx
     kubectl get gateway kc-gateway -n nginx-gateway
     ```

3. Gateway Service의 트래픽 정책과 상태 확인 포트 확인
     #### **lab5-2-3**
     ```bash
     kubectl get service kc-gateway-nginx -n nginx-gateway \
       -o custom-columns=NAME:.metadata.name,TYPE:.spec.type,TRAFFIC-POLICY:.spec.externalTrafficPolicy,HEALTH-CHECK-PORT:.spec.healthCheckNodePort
     ```
     - `TRAFFIC-POLICY`가 `Local`인지 확인

4. nslookup 결과 확인
     - Gateway에서 배포된 서비스(type: LB)의 IP들을 확인 가능
     #### **lab5-2-4**
     ```bash
     kubectl get gateway kc-gateway -n nginx-gateway --watch
     ```
     - `ADDRESS`가 표시되면 `Ctrl+C` 입력
     ```bash
     GATEWAY_ADDRESS=$(kubectl get gateway kc-gateway -n nginx-gateway -o jsonpath='{.status.addresses[0].value}')
     until nslookup ${GATEWAY_ADDRESS} 8.8.8.8; do
       echo "DNS 정보가 반영되기를 기다리는 중입니다."
       sleep 10
     done
     ```
     - Load Balancer 생성 직후에는 DNS 정보 반영에 시간이 걸릴 수 있음


## 3. LoadBalancer 확인

1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > 로드 밸런서
2. Load Balancer 콘솔창에서 AZ별로 생성된 Load Balancer 확인
3. 생성된 두 개의 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
     - `새로운 Public IP를 생성하고 자동으로 할당`
4. 생성된 두 개의 Load Balancer의 Public IP를 복사
5. 브라우저 주소창에 복사한 IP 주소 각각 입력
     - HTTPRoute 배포 전에는 NGINX의 `404 Not Found`가 표시될 수 있음

> Load Balancer 대상이 `Unhealthy`라면 콘솔의 상태 확인 포트와 `HEALTH-CHECK-PORT`가 같은지 확인합니다.
