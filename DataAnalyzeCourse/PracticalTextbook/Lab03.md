# Data Catalog 실습


## 1. Object Storage 버킷 설정
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage > 일반 버킷
2.  `kafka-nginx-log` 버킷 클릭
   - 권한 버튼 클릭
   - 접근 버튼 클릭
      - 접근 설정 버튼 클릭
         - `퍼블릭 액세스 허용 (Read Only) 클릭

3.  `alb-log` 버킷 클릭
   - 권한 버튼 클릭
   - 접근 버튼 클릭
      - 접근 설정 버튼 클릭
         - `퍼블릭 액세스 허용 (Read Only)` 클릭
       
4.  `data-catalog` 버킷 클릭
   - 폴더 생성 버튼 클릭
     - 폴더 이름: `data`
5. 저장 버튼 클릭

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
   - 이름: `dc_database`
   - 경로
      - S3 연결: `체크`
      - 버킷 이름: `data-catalog`
      - 경로: `test`
3. 생성 버튼 클릭


## 4. 테이블 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Catalog > 테이블
2. 테이블 생성 버튼 클릭
- **kafka_data** 테이블
   - 데이터 베이스: `dc_database`
   - 테이블 이름: `kafka_data`
   - 테이블 저장 경로
      - S3 연결: `체크`
      - 버킷 이름: `kafka-nginx-log`(카프카와 연동된 버킷)
      - 디렉터리: `kafka-nginx-log/topics/nginx-topic/partition_0/year_2025/month_02`// 날짜에 맞게 수정
   - 데이터 유형: `JSON`
   - Pub/Sub 연동: `사용`
      - 토픽 선택: `data-catalog-topic`
   - 설명(선택): `없음`
   - 스키마
      - 필드 추가 버튼 클릭
      - 필드 정보
         - 파티션 키: `미사용`
         - 필드 이름: `request`, `method`, `session_id`, `endpoint`, `http_referer`, `query_params`, `status`, `timestamp`
         - 데이터 유형: `string`
         - ---
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
     - 아래와 같이 코드 수정
      ```
      def main():
       # Pull Subscription 이름 설정
       subscription_name = 'data-catalog-pull-sub'
      ```

1. 콘솔에서 이벤트 발생
   - 데이터 속성 추가
   - 스키마 필드 추가
   - 스키마 필드 삭제
     
2. Traffic Generator VM2의 터미널 창에서 실시간 메시지 수신 확인

   

## 6. 크롤러 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data catalog > 크롤러
2. 크롤러 생성 버튼 클릭
    - 데이터베이스: `dc_database`
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

