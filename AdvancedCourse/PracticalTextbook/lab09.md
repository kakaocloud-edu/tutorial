# 오토스케일링 테스트

HPA 옵션을 주어 워크로드 리소스를 자동으로 증가시키는 오토스케일링 실습을 진행합니다.



## 1. HPA 설정

1. 노드의 리소스 사용량을 모니터링하는 metrics-server 설치
  #### **lab9-1-1-1**
   ```bash
   helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
   ```

  #### **lab9-1-1-2**
   ```bash
   helm upgrade --install metrics-server metrics-server/metrics-server --set hostNetwork.enabled=true --set containerPort=4443
   ```

2. HPA.enabled 수정
   - 접속 중인 Bastion VM 인스턴스 터미널에 명령어 입력
   #### **lab9-1-2**
   ```
   sudo vi values.yaml
   ```

   - 40번 라인 수정
     `enabled: false` -> `enabled: true`
   - 43번 라인 수정
     `averageUtilization: 50` -> `averageUtilization: 1`

3. helm upgrade를 통한 릴리즈 업그레이드

   #### **lab9-1-3**
   - 접속 중인 Bastion VM 인스턴스 터미널에 명령어 입력
   ```
   helm upgrade my-release . --description "enable hpa" -f values.yaml
   ```

4. HPA 리소스 생성 확인
   - 접속 중인 Bastion VM 인스턴스 터미널에 명령어 입력
   #### **lab9-1-4**
   ```
   kubectl get all
   ```
5. Pod 확인용 새 터미널 열기

   #### **lab9-1-5-1**
   ```bash
   cd {keypair.pem 다운로드 위치}
   ```

   #### **lab9-1-5-2**
   ```bash
   ssh -i keyPair.pem centos@{bastion의 public ip주소}
   ```
   - **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.
  
   #### **lab9-1-5-3**
   ```bash
   kubectl get po -w
   ```
    
## 2. CPU 부하 발생 및 기능 확인

  1. CPU 부하 발생
  - **Note**: 기존에 사용하던 터미널 창에 아래 코드를 입력해주세요.
  
  #### **lab9-2-1**
  ```bash
  kubectl run -i --tty load-generator --rm --image=ke-container-registry.kr-central-2.kcr.dev/ke-cr/busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://61.109.239.122/; done"
  ```
