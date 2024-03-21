# 기본 환경 구성

기본 환경 구성에 대한 실습입니다.

## 1. VPC 생성 (Demo로 시연됩니다.)

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
4. VPC 생성 확인

## 2. MySQL 인스턴스 그룹 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > MySQL > Instance Group
2. 인스턴스 그룹 만들기 버튼 클릭

   - 이름 : `database`
   - Image : `MySQL 8.0.34`
   - MySQL 사용자 이름: `admin`
   - MySQL 비밀번호 : `admin1234`
     - **Note**: 원활한 실습 진행을 위해 반드시 `admin, admin1234`로 설정해주세요.
   - 인스턴스 가용성 : `고가용성 (Primary, Standby 인스턴스)`
   - 인스턴스 타입 : `m2a.large`
   - 기본 스토리지 크기: `100GB`
   - 로그 스토리지 크기 : `100GB`
   - 네트워크 설정
     - Multi AZ 옵션 : `활성화`
       - VPC : `vpc_1`
       - Subnet : `AZ-a의 Private 서브넷 선택(172.30.16.0/20)`
       - 인스턴스 개수 : 1
       - Subnet : `AZ-b의 Private 서브넷 선택(172.30.48.0/20)`
       - 인스턴스 개수 : 1
   - 자동 백업 미사용
3. 만들기 버튼 클릭
4. MySQL 인스턴스 생성 확인

## 3. 사용자 액세스 키 생성

1. 우측 상단 계정 프로필 > 사용자 액세스 키 > 비밀번호 확인
2. 사용자 액세스 키를 생성해 주세요 클릭
     - 사용자 액세스 키 이름 : `kakaocloud-test`
     - 프로젝트 지정 : `(사용자가 위치한 프로젝트 지정)`
     - 사용자 액세스 키 정보 : `(사용자 선택 입력)`
     - 만료 기한 : `(지정하지 않음)`
3. 만들기 버튼 클릭
4. 사용자 액세스 키 ID 복사 후 클립보드 등에 붙여넣기
5. 사용자 액세스 보안 키 복사 후 클립보드 등에 붙여넣기
  - **Note**: 사용자 액세스 키 만들기 팝업창을 닫은 이후 사용자 액세스 보안 키 정보 다시 조회 불가

