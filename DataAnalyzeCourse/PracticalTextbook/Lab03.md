# Data Catalog 실습


## 1. Object Storage 버킷 설정
1. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
2. `data-catalog` 버킷 설정
      - `data-catalog` 버킷 클릭
         - 권한 탭 클릭
         - 접근 탭 클릭
         - 접근 설정 버튼 클릭
            - 액세스 권한
               - `퍼블릭 액세스 허용 (Read Only)` 선택
               - 접근 허용 IP 주소: 빈칸
               - 저장 버튼 클릭
         - 확인 버튼 클릭
      - `퍼블릭 액세스`가 `허용`으로 됐는지 확인
     

## 2. 카탈로그 생성
1. 카카오 클라우드 콘솔 > Analytics > Data Catalog > 카탈로그
2. 카탈로그 생성 버튼 클릭
   - 이름: `data_catalog`
   - VPC 설정
      - VPC: `kc-vpc`
      - 서브넷: `kr-central-2-a의 Public 서브넷`
      - 생성 버튼 클릭
   - 카탈로그 상태: Running 확인

## 3. 데이터베이스 생성
1. 카카오 클라우드 콘솔 > Analytics > Data Catalog > 데이터베이스
2. 데이터베이스 생성 버튼 클릭
   - 카탈로그: `data_catalog`
   - 이름: `data_catalog_database`
   - 경로
      - S3 연결: `체크`
      - 버킷 이름: `data-catalog`
      - 경로: `data-catalog-dir`
   - 생성 버튼 클릭
   - 카탈로그 상태: Running 확인

## 4. 테이블 생성
1. 카카오 클라우드 콘솔 > Analytics > Data Catalog > 테이블
2. 테이블 생성 버튼 클릭

- **kafka_log_table** 테이블 생성 정보 
   - 데이터 베이스: `data_catalog_database`
   - 테이블 이름: `kafka_log_table`
   - 테이블 저장 경로
      - S3 연결: `체크`
      - 버킷 이름: `data-catalog`
      - 디렉터리: `kafka-nginx-log/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}`
   - 데이터 유형: `JSON`
   - Pub/Sub 연동: `사용`
      - 토픽 선택: `data-catalog-topic`
   - 설명(선택): `없음` 
   - 스키마 
      - 필드 추가 버튼 클릭
      - 필등 정보
         - 파티션 키: `미사용`
         - 컬럼 번호: `1`
         - 필드 이름: `status`
         - 데이터 유형: `string`
         - ---
         - 파티션 키: `미사용`
         - 컬럼 번호: `2`
         - 필드 이름: `query_params`
         - 데이터 유형: `string`
         - --
         - 파티션 키: `미사용`
         - 컬럼 번호: `3`
         - 필드 이름: `endpoint`
         - 데이터 유형: `string`
   - - 생성 버튼 클릭

## 5. Pub/Sub 토픽 생성
![image](https://github.com/user-attachments/assets/dc67c221-fdd1-463b-8a99-24f09ba76611)

1. 카카오 클라우드 콘솔 > Analytics > Pub/Sub > 토픽
2. `data-catalog-topic` 토픽 생성
    - 토픽 생성 버튼 클릭
        - 이름: `data-catalog-topic`
        - 기본 서브스크립션: `생성 안함`
        - 토픽 메세지 보존 기간: `0일 0시 10분`
        - 설명: `없음`
    - 생성 버튼 클릭
3. 생성된 `data-catalog-topic` 클릭
4. `data-catalog-topic`의 Pull 서브스크립션 생성
    - 서브스크립션 탭 클릭
    - 서브스크립션 생성 버튼 클릭
        - 기본 설정
            - 이름: `data-catalog-pull-sub`
            - 토픽 선택: `data-catalog-topic`
        - 유형: `Pull`
        - 서브스크립션 메시지 보존 기간: `0일 0시 10분`
        - 응답 대기 시간: `20초`
        - 재처리 횟수: `횟수 지정`, `3번`
    - 생성 버튼 클릭
5. 서브스크립션의 Active 상태 확인


## 6. 이벤트를 통한 Pub/Sub 연동 확인
1. traffic-generator-2에서 이벤트 메시지 확인

   - **Note**:[`data_catalog_subscribe.py`](https://github.com/kakaocloud-edu/tutorial/new/main/DataAnalyzeCourse/src/day1/Lab02) 

      - 터미널 CLI를 통한 메시지 수신 스크립트 실행
        ```
        /DataAnalyzeCourse/src/day1/Lab02
        ```
        ```
        python3 data_catalog_subscribe.py
        ```

2. 콘솔에서 이벤트 발생
   - 데이터 속성 추가
      - `kafka_log_table` 테이블 클릭
      - 테이블 속성 탭 클릭
      - 테이블 속성 추가하기 버튼 클릭
         - Key: `test_key`
         - Value: `test_value`
      - 추가 버튼 클릭
      - `traffic-generator-2` 터미널 창에서 메시지 정상 수신 및 처리 로그 확인

   - 스키마 필드 추가
      - 스키마 탭 클릭
      - 필드 추가 버튼 클릭
         - 컬럼 번호: `4`
         - 필드 이름: `test_field`
         - 데이터 유형: `string`
         - 설명: `빈칸`
      - 생성 버튼 클릭
      - `traffic-generator-2` 터미널 창에서 메시지 정상 수신 및 처리 로그 확인


## 6. 크롤러 생성
1. 카카오 클라우드 콘솔 > Analytics > Data catalog > 크롤러
2. 크롤러 생성 버튼 클릭
    - 데이터베이스: `data_catalog_database`
    - 크롤러 이름: `crawler`
    - MySQL 전체 경로
        - 연결할 MySQL: `database`
        - MySQL 데이터베이스 이름: `shopdb`
    - MySQL 계정
        - ID: `admin`
        - PW: `admin1234`
        - 연결 테스트 버튼 클릭
    - 설명 (선택): `없음`
    - 테이블 Prefix (선택): `없음`
    - 스케줄: `온디멘드`
    - 생성 버튼 클릭
4. 생성된 크롤러 선택 후 실행
5. 카카오 클라우드 콘솔 > Analytics > Data catalog > 테이블
      - 생성된 테이블 확인

