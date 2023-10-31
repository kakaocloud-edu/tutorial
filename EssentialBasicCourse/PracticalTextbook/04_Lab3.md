# Bastion(점프서버) 및 Web server 인스턴스 생성 실습

Bastion(점프서버) 인스턴스와 Web server 인스턴스를 생성해보고, 점프서버를 통해 웹서버로 접속해보는 실습입니다.

## 1. Bastion VM 인스턴스 생성


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
2. Instance 만들기 클릭
     - 이름 : `bastion`
     - Image : `CentOS 7.9`
     - Instance 타입 : `m2a.large`
     - Volume : `10 GB`
3. 새 Key Pair 생성 클릭
     - 이름 : `keyPair`
     - 만들기 클릭
4. VPC 선택
     - VPC : `vpc_1`
     - Subnet : `main`
     - SecurityGroup 선택
5. 새 Security Group 생성 클릭
     - Security Group 이름: `bastion`
     - Inbound :
       - 프로토콜: `TCP` 
       - 패킷 출발지: `{사용자 IP}/32`
          - **Note**: "사용자_IP" 부분을 실제 IP 주소로 교체하세요.
          - 사용자 IP 조회: [https://www.myip.com/](https://www.myip.com/)
       - 포트 번호: `22` 
6. Outbound 클릭
     - Outbound
          - 프로토콜 : `ALL` 
          - 패킷 목적지 : `0.0.0.0/0`
7. 만들기 버튼 클릭
8. 고급설정 버튼 클릭
     - 사용자 스크립트에 아래 내용 붙여넣기 (mysql client 사용을 위함)
     ```bash
     #!/bin/bash
     sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
     sudo yum localinstall https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm -y
     sudo yum install mysql-community-server -y
     ```
- **Note**: 고급 설정 스크립트 부분을 못하더라도 추후 설정할 수 있습니다.
9. 만들기 버튼 클릭
10. Virtual Machine > Instance
11. 생성된 인스턴스의 우측 메뉴바 > Public IP 연결 클릭
    - `새로운 Public IP를 생성하고 자동으로 할당` 
12. 확인 버튼 클릭
13. 생성된 VPC의 우측 메뉴바 > SSH 연결 클릭
     - SSH 접속 명령어 복사(6. keyPair.pem 파일이 있는 경로에서 아래 명령어를 실행합니다.)
     - Keypair를 다운받아놓은 폴더로 이동
     - 터미널에 명령어 붙여넣기
     - yes 입력

     ```bash
     cd {keyPair.pem 다운로드 위치}
     ```
     ```bash
     chmod 400 keyPair.pem
     ```
     ```bash
     ssh -i keyPair.pem centos@{bastion의 public ip주소}
     ```
     - **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.
     ```bash
     yes
     ```

## 2. Web VM 인스턴스 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
     - bastion 인스턴스의 Private IP 복사
2. Instance 만들기 버튼 클릭
     - 이름 : `web_server_1`
     - Image : `CentOS 7.9`
     - Instance 타입 : `m2a.large`
     - Volume : `10 GB`
     - Key Pair : `keyPair`
3. VPC 선택
     - VPC : `vpc_1`
     - Subnet : `main`
     - 새 Security Group 생성
4. SecurityGroup 만들기
     - Security Group 이름 : `webserver`
     - Inbound 
          - 프로토콜: `TCP`, 패킷 출발지: `0.0.0.0/0`, 포트번호: `80` 
          - 프로토콜: `TCP`, 패킷 출발지: `0.0.0.0/0`, 포트번호: `443`
          - 프로토콜: `TCP`, 패킷 출발지: `{bastion Private IP}/32`, 포트번호: `22` 
          - **Note**: "bastion Private IP" 부분을 복사한 IP 주소로 교체하세요.
          - 프로토콜: `ICMP`, 패킷 출발지: `0.0.0.0/0`
5. Outbound 클릭
     - Outbound
          - 프로토콜 : `ALL` 
          - 패킷 목적지 : `0.0.0.0/0`
6. 만들기 버튼 클릭
7. 고급설정 버튼 클릭
8. 사용자 스크립트에 아래 명령어 붙여넣기
     ```bash
     #!/bin/bash
     yum -y remove mariadb-libs
     yum -y install httpd php mysql php-mysql wget 
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
     - **Note**: 첫번째 '#!/bin/bash'도 적어 주셔야 합니다.
     - **Note**: 스크립트 설정을 못하더라도 추후 설정 가능합니다.
     - 멀티스레딩: 활성화
9. 만들기 버튼 클릭
10. Virtual Machine > Instance > 생성한 인스턴스 ( web_server_1 )의 우측 메뉴바 클릭 > Public IP 연결 클릭
     - `새로운 Public IP를 자동으로 할당` 선택
11. 확인 버튼 클릭

## 3. Bastion VM 인스턴스를 통해 Web 서버 접속


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
2. Virtual Machine > Instance 
3. Bastion VM과  Web Server의 IP 확인하기
     - Bastion의 `Public IP 주소` 확인 및 복사
     - Web_server_1의 `Private IP 주소` 확인 및 복사
4. 터미널 명령어 입력
     - Keypair를 다운받아놓은 폴더로 이동
     - 명령어 붙여넣기
     - yes  입력
     ```bash
     cd {keyPair.pem 다운로드 위치}
     ```
     - **Note**: "{keyPair.pem 다운로드 위치}" 부분을 keyPair.pem의 디렉터리 위치로 교체하세요.
     ```bash
     ssh -i "keyPair.pem" -o ProxyCommand="ssh -W %h:%p centos@{bastion의 public IP} -i keyPair.pem" centos@{web_server_1의 private IP}
     ```
     - **Note**: "{Bastion의 public IP}", "{web_server_1의 private IP}" 부분을 복사한 IP 주소로 교체하세요.
     ```bash
     yes
     ```

## 4. Web VM의 Public IP로 웹 접속 확인


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
2. Virtual Machine > Instance 
3. web_server_1 인스턴스 확인하기
     - Web_server_1의 `Public IP 주소` 확인 및 복사
4. Web_server_1의 `Public IP 주소` 브라우저 창에 입력
     - 생성 지연으로 인해 시간이 조금 지나면 연결이 됩니다.