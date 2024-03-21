# 인그레스 컨트롤러 배포 실습

nginx pod을 위한 deployment, LoadBalancer type의 서비스가 포함된 ingress-nignx controller를 배포하고 ingress-nginx 파드, 서비스, AZ별로 생성된 loadbalancer 확인하는 실습입니다.


## 1. ingress-nignx controller 배포

1. 인그레스 컨트롤러 배포
     - 접속 중인 Bastion VM 인스턴스에 명령어 입력
     #### **lab5-1-1**
     ```bash
     kubectl apply -f https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/ingress-nginx-controller.yaml
     ```
## 2. ingress-nginx 파드 및 서비스 상태 확인

1. ingress-nginx 파드 상태 확인
     - 접속 중인 Bastion VM 인스턴스에 명령어 입력
     #### **lab5-2-1**
     ```bash
     kubectl get all -n ingress-nginx
     ```

2. ingress-nginx 서비스 상태 확인
     #### **lab5-2-2**
     ```bash
     kubectl get svc -n ingress-nginx
     ```
     - **Note**: External-IP의 DNS 주소값 복사(**lab5-2-3** nslookup 다음 위 명령어를 붙여넣습니다.)

3. nslookup 결과 확인
     - ingress-nginx에서 배포된 서비스(type: LB)의 ip들을 확인 가능
     #### **lab5-2-3**
     ```bash
     nslookup {DNS 주소값}
     ```

## 3. LoadBalancer 확인

1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > Load Balancer
2. Load Balancer 콘솔창에서 AZ별로 생성된 Load Balancer 확인
3. 생성된 두 개의 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
     - `새로운 Public IP를 생성하고 자동으로 할당` 
4. 적용 버튼 클릭
5. 생성된 두 개의 Load Balancer의 Public IP를 복사
6. 브라우저 주소창에 복사한 IP 주소 각각 입력
     - nginx에 의한 error 창 확인(404 Not Found)
