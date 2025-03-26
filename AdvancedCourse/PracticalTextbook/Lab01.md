# 기본 환경 구성

기본 환경 구성에 대한 실습입니다.

## 1. VPC 생성 (Demo로 시연됩니다.)

1. 카카오 클라우드 콘솔 > 전체 서비스 > VPC 접속
2. VPC 생성 버튼 클릭
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
3. 생성 버튼 클릭
4. VPC 생성 확인

## 2. MySQL 인스턴스 그룹 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > MySQL > Instance Group
2. 인스턴스 그룹 생성 버튼 클릭

   - 이름 : `database`
   - 인스턴스 가용성 : `고가용성 (Primary, Standby 인스턴스)`
   - 엔진 버전 : `MySQL 8.0.41`
   - Primary 포트 : `3306`
   - Standby 포트 : `3307`
   - MySQL 사용자 이름: `admin`
   - MySQL 비밀번호 : `admin1234`
      - **Note**: 원활한 실습 진행을 위해 반드시 `admin, admin1234`로 설정해주세요.
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
    - 보안 그룹 설정
      - 새 보안 그룹 설정 클릭
        - 보안 그룹 이름: mysql
          - 인바운드
             - 프로토콜: `TCP`, 패킷 출발지: `{교육장의 사설 IP}/32`, 포트 번호: `3306`
             - **Note**: "교육장의 사설 IP" 부분을 실제 IP 주소로 교체하세요.
             - 프로토콜: `TCP`, 패킷 출발지: `0.0.0.0/0`, 포트 번호: `3307`
          - 아웃바운드
             - 프로토콜 : `ALL`, 패킷 목적지 : `0.0.0.0/0`
       - 생성 클릭
   - 자동 백업: `미사용`
   - 테이블 대소문자 구분: `사용`
3. 생성 버튼 클릭
4. MySQL 인스턴스 생성 확인

## 3. IAM 액세스 키 생성

1. 우측 상단 계정 프로필 > 자격 증명
2. 비밀번호 재확인 > 아이디/비밀번호 입력 > 비밀번호 확인
3. IAM 액세스 키 생성 버튼 클릭
     - 프로젝트 : `(사용자가 위치한 프로젝트 지정)`
     - IAM 액세스 키 이름 : `kakaocloud-test`
     - IAM 액세스 키 설명(선택) : `빈 칸`
     - 만료 기한 : `무제한`
4. 생성 버튼 클릭
5. IAM 액세스 키 ID 복사 후 클립보드 등에 붙여넣기
6. IAM 액세스 보안 키 복사 후 클립보드 등에 붙여넣기
  - **Note**: IAM 액세스 키 정보 팝업창을 닫은 이후 IAM 인증 정보 다시 조회 불가

## 4. 키 페어 생성

1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual machine > 키 페어
2. 오른쪽 상단에 있는 `키 페어 생성` 버튼 클릭
3. 키 페어 생성
    - `신규 키 페어 생성하기` 선택
    - 이름: `keypair`
    - `생성` 버튼 클릭
- **Note**: 다운로드 된 private key(e.g. keypair.pem)의 경로 기억하기

