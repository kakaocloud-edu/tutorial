# 리소스 삭제 실습

실습에서 만든 애플리케이션, Gateway API 컨트롤러, Load Balancer와 기타 클라우드 리소스를 의존 관계의 역순으로 삭제합니다. 삭제한 리소스와 데이터는 복구하기 어려울 수 있으므로 실습을 모두 마친 뒤 진행합니다.

## 1. Kubernetes 리소스 삭제

1. Helm으로 설치한 애플리케이션 삭제
   - `helm uninstall`은 `my-release`가 관리하는 Deployment, Service, ConfigMap, Secret, Job, HTTPRoute와 릴리스 이력을 삭제합니다.

   #### **lab11-1**
   ```bash
   helm uninstall my-release
   ```

2. Metrics Server 삭제
   - HPA 실습에서 Helm으로 설치한 `metrics-server` 릴리스와 관련 리소스를 삭제합니다.

   #### **lab11-2**
   ```bash
   helm uninstall metrics-server
   ```

3. Gateway 삭제 및 Load Balancer 삭제 대기
   - 첫 번째 명령은 `kc-gateway`를 삭제합니다. NGINX Gateway Fabric은 이 변경을 감지하여 Gateway 전용 DaemonSet과 LoadBalancer 타입 Service를 함께 삭제합니다.
   - 두 번째 명령은 `kc-gateway-nginx` Service가 완전히 없어질 때까지 기다립니다. Service 삭제가 완료되면 카카오클라우드 Load Balancer 삭제도 시작됩니다.
   - 접속 중인 Bastion VM 인스턴스에서 아래 명령어 입력

   #### **lab11-3**
   ```bash
   kubectl delete -f /home/ubuntu/tutorial/AdvancedCourse/src/manifests/gateway.yaml
   kubectl wait --for=delete service/kc-gateway-nginx -n nginx-gateway --timeout=10m
   ```

4. NGINX Gateway Fabric 삭제
   - Gateway와 데이터 플레인이 사라진 뒤 `ngf` Helm 릴리스를 제거합니다. `--wait`는 컨트롤러 리소스 삭제가 끝날 때까지 기다립니다.

   #### **lab11-4**
   ```bash
   helm uninstall ngf -n nginx-gateway --wait --timeout=5m
   ```

5. NGINX Gateway Fabric 및 Gateway API CRD 삭제
   - 첫 번째 명령은 Helm Chart에 포함된 NGINX Gateway Fabric 전용 CRD를 가져와 클러스터에서 삭제합니다.
   - 두 번째 명령은 Lab05에서 설치한 Gateway API 표준 CRD를 같은 버전의 원본으로 렌더링하여 삭제합니다.
   - 마지막 명령은 전용 네임스페이스가 남아 있을 경우 삭제합니다.

   #### **lab11-5**
   ```bash
   helm show crds oci://ghcr.io/nginx/charts/nginx-gateway-fabric --version 2.3.0 | kubectl delete -f -
   kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.3.0" | kubectl delete -f -
   kubectl delete namespace nginx-gateway --ignore-not-found
   ```

6. 삭제 결과 확인
   - 첫 번째 명령은 전체 네임스페이스의 기본 워크로드를 확인합니다.
   - 두 번째 명령은 LoadBalancer 타입 Service가 남아 있는지 확인합니다.
   - 마지막 명령은 Gateway API 및 NGINX Gateway Fabric CRD가 남아 있으면 출력하고, 없으면 완료 메시지를 표시합니다.

   #### **lab11-6**
   ```bash
   kubectl get all --all-namespaces
   kubectl get service --all-namespaces --field-selector spec.type=LoadBalancer
   kubectl get crd | grep -E 'gateway.networking.k8s.io|gateway.nginx.org' || echo "Gateway 관련 CRD가 모두 삭제되었습니다."
   ```

> Kubernetes Service가 삭제된 뒤 카카오클라우드 콘솔의 Load Balancer가 실제로 사라지기까지 시간이 걸릴 수 있습니다. Load Balancer 삭제를 확인한 다음 연결했던 Public IP를 삭제합니다.

<br>

## 2. 기타 클라우드 리소스 삭제

1. Virtual Machine > Instance > `bastion VM` 선택 > Instance 삭제 > 영구 삭제 > 삭제 버튼 클릭
2. Virtual Machine > 키 페어 > 생성된 키의 오른쪽 (...) 클릭 > 키 페어 삭제
3. DNS > DNS Zone > DNS 이름 클릭 > 추가했던 상단 레코드의 오른쪽 (...) 클릭 > 레코드 삭제 클릭 > 오른쪽 상단 DNS 영역의 오른쪽 (...) 클릭 > DNS 삭제 클릭 > DNS 주소 이름 입력 > 삭제 버튼 클릭
4. Container Registry > Repository > 생성되어 있는 Repository 클릭 > 상단 오른쪽 (...) 클릭 > 리포지토리 삭제 클릭
5. MySQL > Instance Group > 생성되어 있는 인스턴스 그룹 오른쪽 (...) 클릭 > 인스턴스 그룹 삭제 클릭 > 인스턴스 그룹 이름 입력 및 삭제 버튼 클릭
6. Kubernetes Engine > Cluster > 생성되어 있는 클러스터 오른쪽 (...) 클릭 > 클러스터 삭제 클릭
7. VPC > Public IP > 모두 선택 > 삭제 버튼 클릭 > 영구 삭제 입력 > 삭제
8. VPC > 생성되어 있는 VPC 오른쪽 (...) 클릭 > VPC 삭제 > VPC 이름 입력 > 삭제
9. VPC > 보안 그룹 > bastion 보안그룹 선택 > 생성된 보안 그룹의 오른쪽 (...) 클릭 > 보안 그룹 삭제 클릭
10. 오른쪽 상단의 아이콘 클릭 > 자격 증명 클릭 > 생성된 액세스 키의 오른쪽 (...) 클릭 > 삭제 클릭
