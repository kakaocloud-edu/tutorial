# 리소스 삭제 실습

실습에서 만든 애플리케이션, Gateway API 컨트롤러, Load Balancer와 기타 클라우드 리소스를 의존 관계의 역순으로 삭제합니다. 삭제한 리소스와 데이터는 복구하기 어려울 수 있으므로 실습을 모두 마친 뒤 진행합니다.

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
   ```

5. NGINX Gateway Fabric 삭제

   ```bash
   helm uninstall ngf -n nginx-gateway --wait --timeout=5m
   ```

6. NGINX Gateway Fabric 및 Gateway API CRD 삭제
   ```bash
   helm show crds oci://ghcr.io/nginx/charts/nginx-gateway-fabric --version 2.3.0 | kubectl delete -f -
   kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.3.0" | kubectl delete -f -
   kubectl delete namespace nginx-gateway --ignore-not-found
   ```

7. 삭제 결과 확인

   ```bash
   kubectl get all --all-namespaces
   ```

> 📌 Kubernetes Service가 삭제된 뒤 카카오클라우드 콘솔의 Load Balancer가 실제로 사라지기까지 시간이 걸릴 수 있습니다. Load Balancer 삭제를 확인한 다음 연결했던 Public IP를 삭제합니다.

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
4. VPC > Public IP > Bastion VM, 클러스터 노드풀에 연결된 것을 제외하고 모두 선택 > 삭제 버튼 클릭 > 영구 삭제 입력 > 삭제

> ⛔ **클러스터, Bastion VM, VPC, bastion 보안 그룹, 키 페어, 액세스 키는 삭제하지 않습니다.**
