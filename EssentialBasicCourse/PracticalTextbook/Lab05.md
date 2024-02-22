# Private 서브넷 구성 및 MySQL을 통한 DB 구축 실습

Private 서브넷에 MySQL서비스를 이용하여 DB를 구축합니다. 
Bastion 서버에 MySQL DB를 연결할 수 있도록 설정합니다. 
Web서버와 DB간의 연동이 되는지 확인하는 실습입니다.

## 1. MySQL 인스턴스 그룹 생성


1. 카카오 클라우드 콘솔 > 전체 서비스 > MySQL
2. 인스턴스 그룹 만들기
     - 이름 : `database`
     - Image : `MySQL 8.0.34`
     - MySQL 사용자 이름: `admin`
     - MySQL 비밀번호 : `admin1234`
     - 인스턴스 가용성 : `단일(Primary 인스턴스)`
     - 인스턴스 타입 : `m2a.large`
     - 기본 스토리지 크기: `100GB`
     - 로그 스토리지 크기 : `100GB`
     - VPC : `vpc_1`
     - Subnet : `{vpc_1의 Private 서브넷} 선택`
3. 만들기 버튼 클릭

## 2. Bastion에 MySQL 인스턴스 그룹 연결 및 DB 설정


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > Instance 접속
2. bastion의 우측 메뉴바 클릭
- **Note**: bastion 생성 시 고급 설정에 명령어를 넣지 못하였을 때 수행합니다.
     - SSH 연결 
     - SSH 접속 명령어 복사(6. keyPair.pem 파일이 있는 경로에서 아래 명령어를 실행합니다.)
     - Keypair를 다운받아놓은 Downloads 폴더로 이동
     - 터미널 열기
     - 터미널에 명령어 붙여넣기
     - MySQL 연결 명령어 입력
         
     #### **lab5-2-2**
     ```bash
     sudo rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
     sudo yum localinstall https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm -y
     sudo yum module disable mysql -y
     sudo yum install mysql-community-server -y
     ```
3. 카카오 클라우드 콘솔 > 전체 서비스 > MySQL 접속 > database 클릭
     - 엔드포인트 URL 복사
     - **Note**: 아래 명령어를 메모장에 복사한 후 "{엔드포인트URL}" 부분을 복사한 URL 주소로 교체하세요.
          
     #### **lab5-2-3-1**
     ```bash
     mysql --user=admin --password=admin1234 --host={엔드포인트URL} <<EOF
     CREATE DATABASE IF NOT EXISTS myweb;
     USE myweb;
     CREATE TABLE IF NOT EXISTS users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(255) NOT NULL
     );
     INSERT INTO users (username) VALUES ('kakao');
     CALL mysql.mnms_grant_right_user('admin', '%', 'all', '*', '*');
     ALTER USER 'admin'@'%' IDENTIFIED WITH mysql_native_password BY 'admin1234';
     EOF
     ```
     - 명령어에 대한 설명
          - myweb 데이터베이스가 없으면 생성
          - users 테이블이 없으면 myweb 데이터베이스 내에 생성함. 이 테이블은 id (자동 증가, 기본 키)와 username (문자열, 필수) 필드를 포함함.
          - users 테이블에 username 값이 'kakao'인 레코드를 삽입
          - admin 사용자에게 모든 권한을 부여
          - admin 사용자의 인증 방식을 mysql_native_password로 변경하고 비밀번호를 재설정

## 3. Web서버와 DB 연결 확인


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > Instance
2. web_server_1의 `Public IP 주소` 복사
4. 브라우저 창에 `Public IP 주소` 붙여넣기
5. 카카오 클라우드 콘솔 > 전체 서비스 > MySQL > database 클릭
     - 엔드포인트 URL 복사
6. 호스트 입력 칸에 위에서 복사해놓은 엔드포인트 URL을 붙여넣기
     - 유저 이름 가져오기 버튼 클릭
7. 화면에 'kakao'가 출력되면 유저추가 버튼 클릭
8. 유저이름 가져오기 클릭
9. 화면에 'cloud', 'edu'가 추가됨
