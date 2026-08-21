# 리소스 삭제 실습

실습에서 만든 애플리케이션, Gateway API 컨트롤러, Load Balancer와 기타 클라우드 리소스를 의존 관계의 역순으로 삭제합니다. 삭제한 리소스와 데이터는 복구하기 어려울 수 있으므로 실습을 모두 마친 뒤 진행합니다.

> ⚠️ **주의**
> - **Bastion VM은 5일차에서 계속 사용하므로 오늘은 삭제하지 않습니다.** 이에 따라 Bastion VM이 속한 **VPC, bastion 보안 그룹, 키 페어, 액세스 키도 오늘은 삭제하지 않고 5일차로 넘깁니다.**
> - **클러스터도 5일차까지 계속 사용하므로 오늘은 삭제하지 않습니다.** (5일차 끝에서 노드만 정리하고 클러스터 자체는 유지)
> - 아래 섹션1(Kubernetes 리소스 삭제)은 오늘 만든 실습용 애플리케이션·Gateway·NGINX Gateway Fabric 정리이므로 **클러스터를 남기는 것과 상관없이 원래대로 진행**합니다.
> - VPC Public IP를 "모두 선택 후 삭제"할 때 **Bastion VM, 노드풀에 연결된 Public IP는 제외**하고 선택하세요.
> - Kubernetes 리소스는 반드시 **아래 순서(Helm 릴리스 → Gateway → NGINX Gateway Fabric → CRD)대로** 지워야 Load Balancer가 정상적으로 함께 삭제됩니다. 순서를 건너뛰면 Load Balancer가 고아 리소스로 남을 수 있습니다.

## 1. Kubernetes 리소스 삭제

1. Helm으로 설치한 애플리케이션 삭제
   - `helm uninstall`은 `my-release`가 관리하는 Deployment, Service, ConfigMap, Secret, Job, HTTPRoute와 릴리스 이력을 삭제합니다.

   ```bash
   helm uninstall my-release
   ```

2. Helm 외부에서 만든 인증 Secret과 로컬 설정 파일 삭제
   - `regcred`는 Lab06에서 `kubectl`로 직접 생성했기 때문에 `helm uninstall`로 삭제되지 않습니다.
   - 두 번째 명령은 Lab08에서 Helm Chart 디렉터리로 옮긴 `values.yaml`을 Bastion VM에서 삭제합니다. (DB 엔드포인트·비밀번호 포함)

   ```bash
   kubectl delete secret regcred -n default --ignore-not-found
   rm -f /home/ubuntu/tutorial/AdvancedCourse/src/helm/values.yaml
   ```

3. Metrics Server 삭제

   ```bash
   helm uninstall metrics-server
   ```

4. Gateway 삭제 및 Load Balancer 삭제 대기
   - `kc-gateway` 삭제 시 NGINX Gateway Fabric이 Gateway 전용 DaemonSet과 LoadBalancer 타입 Service를 함께 삭제합니다.
   - 두 번째 명령으로 `kc-gateway-nginx` Service가 완전히 없어질 때까지 대기합니다. (완료되면 카카오클라우드 Load Balancer 삭제도 함께 시작됨)

   ```bash
   kubectl delete -f /home/ubuntu/tutorial/AdvancedCourse/src/manifests/gateway.yaml
   kubectl wait --for=delete service/kc-gateway-nginx -n nginx-gateway --timeout=10m
   ```

5. NGINX Gateway Fabric 삭제

   ```bash
   helm uninstall ngf -n nginx-gateway --wait --timeout=5m
   ```

6. NGINX Gateway Fabric 및 Gateway API CRD 삭제
   - ⚠️ 아래 CRD는 클러스터 범위의 공용 API입니다. **이 실습처럼 전용으로 만든 뒤 폐기할 클러스터에서만** 삭제하고, 다른 사용자나 컨트롤러가 함께 쓰는 공유 클러스터에서는 두 CRD 삭제 명령을 건너뜁니다.

   ```bash
   helm show crds oci://ghcr.io/nginx/charts/nginx-gateway-fabric --version 2.3.0 | kubectl delete -f -
   kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.3.0" | kubectl delete -f -
   kubectl delete namespace nginx-gateway --ignore-not-found
   ```

7. 삭제 결과 확인

   ```bash
   kubectl get all --all-namespaces
   kubectl get service --all-namespaces --field-selector spec.type=LoadBalancer
   kubectl get crd | grep -E 'gateway.networking.k8s.io|gateway.nginx.org' || echo "Gateway 관련 CRD가 모두 삭제되었습니다."
   kubectl get secret regcred -n default --ignore-not-found
   test ! -e /home/ubuntu/tutorial/AdvancedCourse/src/helm/values.yaml && echo "로컬 values.yaml이 삭제되었습니다."
   ```

> 📌 Kubernetes Service가 삭제된 뒤 카카오클라우드 콘솔의 Load Balancer가 실제로 사라지기까지 시간이 걸릴 수 있습니다. Load Balancer 삭제를 확인한 다음 연결했던 Public IP를 삭제합니다.

## 2. 기타 클라우드 리소스 삭제

1. DNS > DNS Zone > DNS 이름 클릭 > 추가했던 상단 레코드의 오른쪽 (...) 클릭 > 레코드 삭제 클릭 > 오른쪽 상단 DNS 영역의 오른쪽 (...) 클릭 > DNS 삭제 클릭 > DNS 주소 이름 입력 > 삭제 버튼 클릭
2. Container Registry > Repository > 생성되어 있는 Repository 클릭 > 상단 오른쪽 (...) 클릭 > 리포지토리 삭제 클릭
3. MySQL > Instance Group > 생성되어 있는 인스턴스 그룹 오른쪽 (...) 클릭 > 인스턴스 그룹 삭제 클릭 > 인스턴스 그룹 이름 입력 및 삭제 버튼 클릭
4. VPC > Public IP > Bastion VM, 클러스터 노드풀에 연결된 것을 제외하고 모두 선택 > 삭제 버튼 클릭 > 영구 삭제 입력 > 삭제

> ⛔ **클러스터, Bastion VM, VPC, bastion 보안 그룹, 키 페어, 액세스 키는 삭제하지 않습니다.**
