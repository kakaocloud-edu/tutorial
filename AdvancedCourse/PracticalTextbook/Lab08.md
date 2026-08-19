# Kubernetes Engine 클러스터에 웹서버 자동화 배포하기

지금까지 YAML 파일로 직접 배포한 애플리케이션을 Helm Chart로 패키징하여 배포, 업데이트, 롤백하는 실습입니다. Chart에는 Deployment, Service, ConfigMap, Secret, Job, HTTPRoute가 템플릿으로 정의되어 있으며 `values.yaml` 값에 따라 실제 Kubernetes 리소스가 만들어집니다.

## 1. 기존 리소스 삭제

1. YAML 파일로 배포한 리소스 삭제
   - `kubectl delete -f`는 Lab06에서 적용한 YAML을 기준으로 애플리케이션 리소스를 삭제합니다. 다음 단계에서 같은 역할의 리소스를 Helm으로 다시 배포하기 위한 정리 작업입니다.

   #### **lab8-1-1**
   ```bash
   kubectl delete -f ./lab6-manifests.yaml
   ```

2. 실습에 사용한 YAML 파일 삭제
   - `rm -f`는 Bastion VM에 복사해 둔 매니페스트를 삭제합니다. `-f` 옵션은 파일이 이미 없어도 오류를 표시하지 않습니다.

   #### **lab8-1-2**
   ```bash
   rm -f lab6-manifests.yaml
   ```

3. 리소스 삭제 결과 확인
   - 다음 명령은 Lab06에서 배포한 Route와 워크로드가 남아 있는지 한 번에 확인합니다. Helm에서도 사용할 `regcred` Secret은 남아 있어야 합니다.

   #### **lab8-1-3**
   ```bash
   kubectl get httproute,service,deployment,pod,job,configmap,secret
   ```

## 2. Helm CLI 확인

1. Helm이 없을 때만 설치
   - `command -v helm`으로 실행 파일을 찾고, 설치되어 있지 않을 때만 파이프 뒤의 Helm 공식 설치 스크립트를 실행합니다. Lab05에서 이미 설치했다면 설치 과정은 건너뜁니다.

   #### **lab8-2-1**
   ```bash
   command -v helm >/dev/null || curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | sudo bash
   ```

2. 설치된 Helm 버전 확인
   - Helm 클라이언트의 버전 정보가 정상적으로 출력되는지 확인합니다.

   #### **lab8-2-2**
   ```bash
   helm version
   ```

## 3. Helm Chart 프로젝트 설정

1. Chart 디렉터리로 이동
   - `Chart.yaml`과 `templates` 디렉터리가 있는 실습용 Chart 루트로 이동합니다.

   #### **lab8-3-1**
   ```bash
   cd /home/ubuntu/tutorial/AdvancedCourse/src/helm
   ```

2. 실습 환경 값이 반영된 `values.yaml` 배치
   - Lab03의 초기화 스크립트가 레지스트리 이미지 주소와 데이터베이스 엔드포인트를 반영해 `/home/ubuntu/values.yaml`을 만들었습니다.
   - 이 명령은 해당 파일을 Chart 루트로 옮겨 Helm 템플릿의 입력값으로 사용합니다.

   #### **lab8-3-2**
   ```bash
   sudo mv /home/ubuntu/values.yaml ./values.yaml
   ```

## 4. Chart 구조 확인

1. `tree`를 이용해 Chart 파일 확인
   - 디렉터리 구조를 트리 형태로 출력합니다. `templates/httproute.yaml`을 포함한 각 Kubernetes 리소스 템플릿이 있는지 확인합니다.

   #### **lab8-4-1**
   ```bash
   tree .
   ```

## 5. Chart 문제 검사

1. Helm lint 실행
   - `helm lint`는 Chart 메타데이터, 템플릿 문법, values 참조에 기본적인 오류가 있는지 검사합니다. `0 chart(s) failed`가 출력되는지 확인합니다.

   #### **lab8-5-1**
   ```bash
   helm lint .
   ```

## 6. Chart 설치 시뮬레이션 및 설치

1. 설치 전 템플릿 렌더링
   - `helm template`은 클러스터에 아무것도 생성하지 않고 템플릿과 `values.yaml`을 합쳐 최종 Kubernetes YAML을 출력합니다.
   - 출력에 `kind: HTTPRoute`가 있고 `parentRefs`가 `kc-gateway`를 가리키는지 확인합니다.

   #### **lab8-6-1**
   ```bash
   helm template my-release . -f values.yaml
   ```

2. Dry Run으로 설치 과정 점검
   - `--dry-run --debug`는 실제 설치 없이 릴리스 생성 과정을 시뮬레이션합니다. `tee`는 결과를 화면에 보여 주면서 `/home/ubuntu/yamls` 파일에도 저장합니다.

   #### **lab8-6-2**
   ```bash
   helm install --dry-run --debug my-release . -f values.yaml | tee ~/yamls
   ```

3. Chart 설치
   - `my-release`라는 이름으로 Chart를 설치합니다. Helm은 렌더링한 Deployment, Service, ConfigMap, Secret, Job, HTTPRoute를 클러스터에 생성하고 릴리스 이력을 저장합니다.

   #### **lab8-6-3**
   ```bash
   helm install my-release . -f values.yaml
   ```

4. 릴리스와 세부 상태 확인
   - `helm list`는 현재 네임스페이스에 설치된 릴리스 목록을 보여 줍니다.
   - `helm status`는 `my-release`가 관리하는 리소스와 현재 배포 상태를 보여 줍니다.

   #### **lab8-6-4**
   ```bash
   helm list
   helm status my-release
   ```
   - `my-release`의 `STATUS`가 `deployed`인지 확인합니다.

5. 워크로드와 HTTPRoute 상태 확인
   - 첫 번째 명령은 Helm으로 생성된 워크로드와 Service의 준비 상태를 보여 줍니다.
   - 두 번째와 세 번째 명령은 Helm이 만든 HTTPRoute와 Gateway 연결 조건을 확인합니다.

   #### **lab8-6-5**
   ```bash
   kubectl get all
   kubectl get httproute
   kubectl get httproute my-release-kc-spring-demo-route \
     -o jsonpath='{range .status.parents[*].conditions[*]}{.type}={.status}{"\n"}{end}'
   ```
   - HTTPRoute의 `Accepted=True`, `ResolvedRefs=True`를 확인합니다.
   - Load Balancer의 Public IP로 접속한 뒤 새로 고침하여 `my-release-kc-spring-demo-...` 형식의 Pod 이름이 화면에 표시되는지 확인합니다.

## 7. Helm Chart를 이용한 버전 관리

1. `replicaCount` 수정
   - `vi` 편집기로 `values.yaml`을 열고 첫 번째 줄의 `replicaCount: 2`를 `replicaCount: 3`으로 변경합니다.
   - `Esc`를 누른 뒤 `:wq`와 Enter를 입력하여 저장하고 종료합니다.

   #### **lab8-7-1**
   ```bash
   sudo vi values.yaml
   ```

2. Chart 릴리스 업그레이드
   - `helm upgrade`는 변경한 values를 다시 렌더링하여 기존 `my-release`에 적용합니다. `--description`은 이 변경의 목적을 릴리스 이력에 기록합니다.

   #### **lab8-7-2**
   ```bash
   helm upgrade my-release . --description "#pod 2->3" -f values.yaml
   ```

3. 릴리스 Revision 확인
   - 상태에서 `REVISION`이 `2`로 증가하고 `STATUS`가 `deployed`인지 확인합니다.

   #### **lab8-7-3**
   ```bash
   helm status my-release
   ```

4. Pod 개수 변경 확인
   - 업그레이드 결과로 애플리케이션 Pod가 3개가 되었는지 확인합니다.

   #### **lab8-7-4**
   ```bash
   kubectl get pod
   ```

5. 릴리스 이력 확인
   - `helm history`는 최초 설치와 업그레이드를 Revision 단위로 보여 줍니다.

   #### **lab8-7-5**
   ```bash
   helm history my-release
   ```

6. Revision별 values 비교
   - 각 명령은 해당 Revision에서 실제 사용한 values를 출력합니다. Revision 1의 `replicaCount`는 `2`, Revision 2는 `3`인지 비교합니다.

   #### **lab8-7-6-1**
   ```bash
   helm get values my-release --revision 1
   ```

   #### **lab8-7-6-2**
   ```bash
   helm get values my-release --revision 2
   ```

## 8. 롤백

1. 최초 Revision으로 롤백
   - `helm rollback my-release 1`은 Revision 1의 리소스 설정으로 되돌립니다. 롤백 작업 자체도 새로운 Revision으로 기록됩니다.

   #### **lab8-8-1**
   ```bash
   helm rollback my-release 1
   ```

2. 롤백 이력 확인
   - 가장 최근 Revision의 설명과 상태를 확인합니다.

   #### **lab8-8-2**
   ```bash
   helm history my-release
   ```

3. Pod 수 감소 확인
   - 최초 설정으로 돌아가 애플리케이션 Pod가 다시 2개가 되었는지 확인합니다.

   #### **lab8-8-3**
   ```bash
   kubectl get pod
   ```
