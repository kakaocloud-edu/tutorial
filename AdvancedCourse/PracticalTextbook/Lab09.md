# HPA (Horizontal Pod Autoscaler) 테스트
HPA 옵션을 주어 워크로드 리소스를 자동으로 증가시키는 오토스케일링 실습을 진행합니다.



## 1. HPA 설정

1. metrics-server 저장소 추가
   #### **lab9-1-1**
   ```bash
   helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
   ```

2. 노드의 리소스 사용량을 모니터링하는 metrics-server 설치
   #### **lab9-1-2**
   ```bash
   helm upgrade --install metrics-server metrics-server/metrics-server --set hostNetwork.enabled=true --set containerPort=4443
   ```

3. HPA.enabled 수정
   - 접속 중인 Bastion VM 인스턴스 터미널에 명령어 입력
   #### **lab9-1-3**
   ```
   sudo vi values.yaml
   ```
   - `hpa.enabled`의 값을 `false`에서 `true`로 변경

4. helm upgrade를 통한 릴리즈 업그레이드

   #### **lab9-1-4**
   - 접속 중인 Bastion VM 인스턴스 터미널에 명령어 입력
   ```
   helm upgrade my-release . --description "enable hpa" -f values.yaml
   ```

5. HPA 리소스 생성 확인
   - 접속 중인 Bastion VM 인스턴스 터미널에 명령어 입력
   #### **lab9-1-5**
   ```
   kubectl get all
   ```
6. Pod 확인용 새 터미널 열기

   #### **lab9-1-6**
   ```bash
   cd {keypair.pem 다운로드 위치}
   ```

- **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.
   ```bash
   ssh -i keypair.pem ubuntu@{bastion의 public ip주소}
   ```
  
   ```bash
   kubectl get po -w
   ```
    
## 2. CPU 부하 발생 및 기능 확인

  1. CPU 부하 발생
  - **Note**: 기존에 사용하던 터미널 창 이용
  - **Note**: 아래 코드에서 `{웹서비스를 위한 Public IP}`에 LB에 할당된 Public IP 중에 하나로 대체하여 아래 명령을 실행
  
    #### **lab9-2-1**
    ```bash
    kubectl run -i --tty load-generator --rm --image=ke-container-registry.kr-central-2.kcr.dev/ke-cr/busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://{웹서비스를 위한 Public IP}/; done"
    ```
    
  2. pod 자동확장 여부 확인
  - **Note**: 5번에서 열었던 터미널 창에서 결과를 확인해 주세요.
  
  - 리소스 사용량에 맞추어 pod이 자동확장 되는 것을 확인
   


   

