# Bastion(점프서버) 및 Web server 인스턴스 생성 실습

Bastion(점프서버) 인스턴스와 Web server 인스턴스를 생성해보고, 점프서버를 통해 웹서버로 접속해보는 실습입니다.

## 1. Bastion VM 인스턴스 생성


1. 전체 서비스 > Virtual Machine 접속
2. Virtual Machine > Instance > Instance 만들기
     - 이름 : `bastion`
     - Image : `CentOS 7.9`
     - Instance 타입 : `m2a.large`
     - Volume : `10 GB`
3. 새 Key Pair 생성 클릭
     - 이름 : `keyPair`
     - 만들기 클릭
     - 생성한 키페어 선택
4. VPC 선택
     - VPC : `vpc_1`
     - Subnet : `main`
     - 새 Security Group 생성
5. SecurityGroup 선택
     - Inbound :
       - 프로토콜: `TCP` 
       - 패킷 출발지: `사용자 IP/32`
         - **Note**: "사용자_IP" 부분을 실제 IP 주소로 교체하세요.
         - 사용자 IP 조회: [https://www.myip.com/](https://www.myip.com/)
       - 포트 번호: `22` 
     - Outbound
       - 프로토콜 : `ALL` 
       - 패킷 목적지 : `0.0.0.0/0`
     - Security Group 선택확인
6. 고급설정 > 사용자 스크립트에 아래 내용 붙여넣기 (mysql client 사용을 위함)

    ```bash
    #!/bin/bash
    sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
    sudo yum localinstall https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm -y
    sudo yum install mysql-community-server -y
    ```