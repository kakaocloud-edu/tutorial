# 웹서버 이중화 및 LB 구성 실습

Public 서브넷에 Web서버 VM을 하나 더 생성합니다. 만든 Web서버와 DB간의 연결이 되는지 확인합니다.
 Load Balancer를 생성하고 2개의 Web 서버 VM과 연결합니다. Load Balancer가 트래픽을 잘 분배하는지 볼 수 있는 실습입니다.
```mermaid
graph LR
    시작(시작) --> Web2VM생성(Web2 VM 인스턴스 생성)
    Web2VM생성 --> Web2DB연결(Web2 서버와 DB 연결)
    Web2DB연결 --> LB생성(Load Balancer 생성)
    LB생성 --> 타겟그룹설정(Target Group 설정)
    타겟그룹설정 --> 웹접속및밸런싱확인(웹 접속 및 밸런싱 여부 확인)
    웹접속및밸런싱확인 --> 종료(종료)

    %% 강조
    class Web2VM생성,Web2DB연결,LB생성,타겟그룹설정,웹접속및밸런싱확인 emphasized;
    
    %% 클래스 스타일
    classDef emphasized fill:#f9f,stroke:#333,stroke-width:4px;

```

## 1. Web2 VM 인스턴스 생성


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > Instance
2. 인스턴스 만들기 클릭
     - 이름 : `web_server_2`
     - 개수 : `1`
     - Image : `Ubuntu 20.04 - 5.4.0-173`
     - Instance 타입 : `m2a.large`
     - Volume : `30 GB`
     - Key Pair : `keypair`
     - VPC : `vpc_1`
     - Subnet : `main`
     - Security Group : `webserver`
3. 고급 설정 클릭
     - 내부 스크립트 복사 후 클립보드에 보관
      
     #### **lab6-1-3**
     ```bash
     #!/bin/bash
     yum -y remove mariadb-libs
     yum -y install httpd php mysql php-mysqlnd wget 
     systemctl enable httpd
     cd /var/www/html
     wget https://github.com/kimjaehyeon0314/test/raw/main/kakao.tar.gz -O kakao.tar.gz
     tar -xvf kakao.tar.gz
     mv /var/www/html/kakao/{index.php,get_user_list.php,add_user.php} /var/www/html/
     rm /etc/selinux/config
     mv /var/www/html/kakao/config /etc/selinux
     setenforce 0
     systemctl start httpd
     ```
4. 만들기 버튼 클릭
5. 전체 서비스 > Virtual Machine > Instance
6. web_server_2의 우측 메뉴바 클릭 > Public IP 연결 클릭
     - `새로운 Public IP를 자동으로 할당` 선택
7. 확인 버튼 클릭
8. Web_server_2의 {Public IP} 복사 후 브라우저 창에 입력
    
> 💡 고급설정에서 스크립트 입력을 못했을 경우 VM에 접속하여 아래 명령어 붙여넣기

```bash
#!/bin/bash
sudo yum -y remove mariadb-libs
sudo yum -y install httpd php mysql php-mysqlnd wget 
sudo systemctl enable httpd
cd /var/www/html
sudo wget https://github.com/kimjaehyeon0314/test/raw/main/kakao.tar.gz -O kakao.tar.gz
sudo tar -xvf kakao.tar.gz
sudo mv /var/www/html/kakao/{index.php,get_user_list.php,add_user.php} /var/www/html/
sudo rm /etc/selinux/config
sudo mv /var/www/html/kakao/config /etc/selinux
sudo setenforce 0
sudo systemctl start httpd
```

## 2. Web2 서버와 DB 연결


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > Instance
2. Web_server_2의 {Public IP} 복사 후 브라우저 창에 입력
3. 카카오 클라우드 콘솔 > 전체 서비스 > MySQL > database 클릭
     - 엔드포인트 URL 복사
4. 호스트 입력 칸에 위에서 복사해놓은 엔드포인트 URL을 붙여넣기
     - 유저 이름 가져오기 버튼 클릭
     - kakao cloud edu가 추가되는지 확인
5. 유저 추가 버튼 클릭
6. 유저 이름 가져오기 버튼 클릭
     - 유저 ‘cloud’와 ‘edu’가 다시 추가되는지 확인

## 3. Load Balancer 생성 및 설정


1. 카카오 클라우드 콘솔 > 전체 서비스 > Load Balancing
2. Load Balancer 만들기 버튼 클릭
     - 타입 선택 : `Application Load Balancer`
     - Load Balancer 이름 : `App_LB`
     - VPC : `vpc_1`
     - Subnet : `main`
     - Listener : `HTTP` : `80`
3. 만들기 버튼 클릭
4. 카카오 클라우드 콘솔 > 전체 서비스 > Load Balancing
5. Target Group 클릭
6. Target Group 만들기 버튼 클릭
     - Availability Zone : `kr-central-2-a`
     - Load Balancer : `App_LB`
     - Listener : `HTTP : 80`
     - Target Group 이름 : `App_Target`
     - 프로토콜 : `HTTP`
     - 알고리즘 : `Round Robin`
     - Sticky Session : `미사용`
     - Health Check : `사용`
     - 타입 : `HTTP`
7. 다음 버튼 클릭
8. 체크 박스 선택
     - web_server_1(Instance), web_server_2(Instance) 좌측 체크 박스 선택
9. 하단 포트:`80`
10. Target 추가 버튼 클릭
11. 다음 버튼 클릭
12. 만들기 버튼 클릭
13. 카카오 클라우드 콘솔 > 전체 서비스 > Load Balancing
14. App_LB 우측 메뉴바 아이콘 클릭
15. Public IP 연결 버튼 클릭
     - `새로운 Public IP를 생성하고 자동으로 할당` 선택
16. 적용 버튼 클릭
17. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > Instance
18. web_server_1, web_server_2의 우측 메뉴바 클릭 > Public IP 연결 해제 를릭

## 4. 웹 접속 및 밸런싱 여부 확인


1. 카카오 클라우드 콘솔 > 전체 서비스 > Load Balancing
2. App_LB의 Public IP 주소 복사
3. 브라우저 주소창에 복사한 IP 주소 입력
     - 몇 분후 새로고침 시 호스트명이 바뀌는 것을 확인합니다.
