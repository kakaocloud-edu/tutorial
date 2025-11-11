# 인그레스 컨트롤러 배포 실습

nginx pod을 위한 deployment, LoadBalancer type의 서비스가 포함된 ingress-nginx controller를 배포하고 ingress-nginx 파드, 서비스, AZ별로 생성된 loadbalancer 확인하는 실습입니다.


## 1. <a href="https://github.com/kakaocloud-edu/tutorial/blob/main/AdvancedCourse/src/manifests/ingress-nginx-controller.yaml" target="_blank">ingress-nginx controller</a> 배포 (Demo)

1. 인그레스 컨트롤러 배포
     - 접속 중인 Bastion VM 인스턴스에 명령어 입력
     #### **lab5-1-1**
     ```bash
     kubectl apply -f https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/ingress-nginx-controller.yaml
     ```
## 2. ingress-nginx 파드 및 서비스 상태 확인

1. ingress-nginx 자원들의 상태 확인
     - 접속 중인 Bastion VM 인스턴스에 명령어 입력
     #### **lab5-2-1**
     ```bash
     kubectl get all -n ingress-nginx
     ```
     - 아래와 같은 상태가 정상적인 완료 상태
       ![image](https://github.com/kakaocloud-edu/tutorial/assets/128004136/e417ff0c-5a9c-467c-874a-961b15d375c7)

2. nslookup 결과 확인
     - ingress-nginx에서 배포된 서비스(type: LB)의 ip들을 확인 가능
     #### **lab5-2-3**
     ```bash
     nslookup {DNS 주소값}
     ```
     ![image](https://github.com/kakaocloud-edu/tutorial/assets/128004136/f0b6f79e-61e8-42cf-b3e2-36701036cd65)
     

## 3. LoadBalancer 확인

1. 카카오 클라우드 콘솔 > 전체 서비스 > Beyond Networking Service > Load Balancing > 로드 밸런서
2. Load Balancer 콘솔창에서 AZ별로 생성된 Load Balancer 확인
   ![image](https://github.com/kakaocloud-edu/tutorial/assets/128004136/1d0969d5-1bd3-4db1-8c08-03da0c6a3dd6)
3. 생성된 두 개의 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
     - `새로운 Public IP를 생성하고 자동으로 할당`
   ![image](https://github.com/kakaocloud-edu/tutorial/assets/128004136/086debda-f9c2-40d7-9d07-b86b322ce6f1)
4. 생성된 두 개의 Load Balancer의 Public IP를 복사
5. 브라우저 주소창에 복사한 IP 주소 각각 입력
     - nginx에 의한 error 창 확인(404 Not Found)
