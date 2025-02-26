# Data Catalog 실습


## 1. Object Storage 버킷 설정
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage > 일반 버킷
2. `kafka-nginx-log` 버킷 설정
      - kafka-nginx-log` 버킷 클릭
      - 권한 탭 클릭
      - 접근 탭 클릭
      - 접근 설정 버튼 클릭
         - 액세스 권한
            - `퍼블릭 액세스 허용 (Read Only)` 선택
         - 접근 허용 IP 주소: 빈칸
      - 저장 버튼 클릭
      - 확인 버튼 클릭

3. `alb-log` 버킷 설정
   - `alb-log` 버킷 클릭
   - 권한 탭 클릭
   - 접근 탭 클릭
   - 접근 설정 버튼 클릭
      - 액세스 권한
         - `퍼블릭 액세스 허용 (Read Only)` 선택
      - 접근 허용 IP 주소: 빈칸
   - 저장 버튼 클릭
   - 확인 버튼 클릭
     

## 2. 카탈로그 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Catalog > 카탈로그
2. 카탈로그 생성 버튼 클릭

   - 이름: `data_catalog`
   - VPC 설정
      - VPC: `kc-vpc`
      - 서브넷: `kr-central-2-a의 Public 서브넷`

3. 생성 버튼 클릭


## 3. 데이터베이스 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Catalog > 데이터베이스
2. 데이터베이스 생성 버튼 클릭
   - 카탈로그: `data_catalog`
   - 이름: `data_catalog_database`
   - 경로
      - S3 연결: `체크`
      - 버킷 이름: `data-catalog`
      - 경로: `tables`
3. 생성 버튼 클릭


## 4. 테이블 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Catalog > 테이블
2. 테이블 생성 버튼 클릭
- **kafka_data_table** 테이블 정보
   - 데이터 베이스: `data_catalog_database`
   - 테이블 이름: `kafka_data_table`
   - 테이블 저장 경로
      - S3 연결: `체크`
      - 버킷 이름: `kafka-nginx-log`(카프카와 연동된 버킷)
      - 디렉터리: `topics/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}`
   - 데이터 유형: `JSON`
   - Pub/Sub 연동: `사용`
      - 토픽 선택: `data-catalog-topic`
   - 설명(선택): `없음` 
   - 스키마 (## 지만 - 보기 좋게 수정, 필요한 값들 넣기, alb_data_table 테이블 정보 넣기##)
      - 필드 추가 버튼 클릭
         - 파티션 키: `미사용`
         - 컬럼 번호: `1`
         - 필드 이름: `request`
         - 데이터 유형: `string`
      - 생성 버튼 클릭
      - 필드 추가 버튼 클릭
         - 파티션 키: `미사용`
         - 컬럼 번호: `2`
         - 필드 이름: `method`
         - 데이터 유형: `string`
      - 생성 버튼 클릭
      - 필드 추가 버튼 클릭
         - 파티션 키: `미사용`
         - 컬럼 번호: `3`
         - 필드 이름: `session_id`
         - 데이터 유형: `string`
      - 생성 버튼 클릭
      - 필드 추가 버튼 클릭
         - 파티션 키: `미사용`
         - 컬럼 번호: `4`
         - 필드 이름: `endpoint`
         - 데이터 유형: `string`
      - 생성 버튼 클릭
      - 필드 추가 버튼 클릭
         - 파티션 키: `미사용`
         - 컬럼 번호: `5`
         - 필드 이름: `http_referer`
         - 데이터 유형: `string`
      - 생성 버튼 클릭
      - 필드 추가 버튼 클릭
         - 파티션 키: `미사용`
         - 컬럼 번호: `6`
         - 필드 이름: `query_params`
         - 데이터 유형: `string`
      - 생성 버튼 클릭
      - 필드 추가 버튼 클릭
         - 파티션 키: `미사용`
         - 컬럼 번호: `7`
         - 필드 이름: `status`
         - 데이터 유형: `string`
      - 생성 버튼 클릭
      - 필드 추가 버튼 클릭
         - 파티션 키: `미사용`
         - 컬럼 번호: `8`
         - 필드 이름: `timestamp`
         - 데이터 유형: `string`
      - 생성 버튼 클릭


- **alb_data_table** 테이블 정보

3. 생성 버튼 클릭


## 5. Pub/Sub 메시지 확인
1. pub/sub 연동을 통한 메시지 확인


   ### Traffic Generator VM2에서 메시지 확인 코드 실행
   - 기존에 사용하던 `restapi_pull_sub.py`에서 subscription 이름만 `data-catalog-pull-sub`로 변경
   - **Note**:[`restapi_pull_sub.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM2/restapi_pull_sub.py) 코드 재사용
      ```
      cd /home/ubuntu/syu-DataAnalyze/TrafficGenerator/REST_API/VM2
      ```
      ```
      vi restapi_pull_sub.py
      ```
      - **Note**: i(입력 모드) 누른 후 화면 하단에--INSERT-- 확인 후 수정
      - **Note**: esc(명령 모드) 누른 후 :wq로 저장
      - 아래와 같이 코드 수정
      ```
      def main():
       # Pull Subscription 이름 설정
       subscription_name = 'data-catalog-pull-sub'
      ```
      - 터미널 CLI를 통한 메시지 수신 스크립트 실행
      ```
      python3 restapi_pull_sub.py
      ```

1. 콘솔에서 이벤트 발생
   - 데이터 속성 추가
      - `kafka_data` 테이블 클릭
      - 테이블 속성 탭 클릭
      - 테이블 속성 추가하기 버튼 클릭
         - Key: `test_key`
         - Value: `test_value`
      - 추가 버튼 클릭
      - `traffic-generator-2` 터미널 창에서 메시지 정상 수신 및 처리 로그 확인

   - 데이터 속성 삭제
      - `test_key` 우측 `⋮` 버튼 클릭
      - 삭제 버튼 클릭
      - `traffic-generator-2` 터미널 창에서 메시지 정상 수신 및 처리 로그 확인

   - 스키마 필드 추가
      - 스키마 탭 클릭
      - 필드 추가 버튼 클릭
         - 컬럼 번호: `9`
         - 필드 이름: `test_field`
         - 데이터 유형: `string`
         - 설명: `빈칸`
      - 생성 버튼 클릭
      - `traffic-generator-2` 터미널 창에서 메시지 정상 수신 및 처리 로그 확인

   - 스키마 필드 삭제
      - `test_field` 스키마 우측 `⋮` 버튼 클릭
      - 삭제 버튼 클릭
      - `traffic-generator-2` 터미널 창에서 메시지 정상 수신 및 처리 로그 확인
   

## 6. 크롤러 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data catalog > 크롤러
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
3. 생성 버튼 클릭
4. 생성된 크롤러 선택 후 실행
5. 카카오 클라우드 콘솔 > 전체 서비스 > Data catalog > 테이블
      - 생성된 테이블 확인

