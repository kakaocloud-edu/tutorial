# 기본 환경 구성

기본 환경 구성에 대한 실습입니다.

## 1. VPC 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > VPC 접속
2. VPC 만들기 버튼 클릭
   - VPC 정보
     - VPC 이름 : `vpc_1`
     - VPC IP CIDR 블록 : `172.30.0.0/16`
   - Availability Zone
     - AZ 개수 : `2`
     - 첫 번째 AZ : `kr-central-2-a`
     - 두 번째 AZ : `kr-central-2-b`
   - Subnet 설정
     - AZ당 Public Subnet 개수 : `1`
     - AZ당 Private Subnet 개수 : `1`
     - kr-central2-a의 Public Subnet IPv4 CIDR 블록 : `172.30.0.0/20`
     - kr-central2-a의 Private Subnet IPv4 CIDR 블록 : `172.30.16.0/20`
     - kr-central2-b의 Public Subnet IPv4 CIDR 블록 : `172.30.32.0/20`
     - kr-central2-b의 Private Subnet IPv4 CIDR 블록 : `172.30.48.0/20`
3. 만들기 버튼 클릭

## 2. Container Registry 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > VPC 접속
2. 리포지토리 만들기 버튼 클릭
   - 공개 여부: 비공개
   - 리포지토리 이름 : `kakao-registry`
   - 태그 덮어쓰기 : 가능
   - 이미지 스캔 : 자동
3. 만들기 버튼 클릭

# 3. MYSQL 인스턴스 그룹 생성

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
   - 네트워크 설정

     - Multi AZ 옵션 : 활성화

       - VPC : `vpc_1`
       - Subnet : `{AZ-a의 Private 서브넷} 선택`
       - 인스턴스 개수 : 1

       - Subnet : `{AZ-b의 Private 서브넷} 선택`
       - 인스턴스 개수 : 1

3. 만들기 버튼 클릭
