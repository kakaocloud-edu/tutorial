# Data Catalog 실습

Data Catalog와 Pub/Sub, Object Storage를 연동해 테이블 생성 및 이벤트 처리와 크롤러를 통한 MySQL 메타데이터 추출을 수행하는 실습입니다.

---

## 1. Object Storage 버킷 권한 설정
1. 카카오 클라우드 콘솔 > Beyond Storage Service > Object Storage > 일반 버킷
2. `data-catalog-bucket` 버킷 설정
      - `data-catalog-bucket` 버킷 클릭
         - 권한 탭 클릭
         - 접근 탭 클릭
         - 접근 설정 버튼 클릭
            - 액세스 권한
               - `퍼블릭 액세스 허용 (Read Only)` 선택
               - 접근 허용 IP 주소: 빈 칸
               - 저장 버튼 클릭
         - 확인 버튼 클릭
3. `퍼블릭 액세스`가 `허용 (Read Only)`으로 바뀐 것을 확인
![1](https://github.com/user-attachments/assets/dade13de-cdd4-42f9-a1a6-0795281e093b)


## 2. Data Catalog 실습용 Pub/Sub 리소스 생성
![image](https://github.com/user-attachments/assets/6fde6a89-5c5a-4153-8512-6dca577d59c9)

1. 카카오 클라우드 콘솔 > Analytics > Pub/Sub > 토픽
2. 토픽 생성 버튼 클릭
      - 이름: `data-catalog-topic`
      - 기본 서브스크립션: `생성 안함`
      - 토픽 메세지 보존 기간: `0일 0시 10분`
      - 설명: 빈 칸
      - 생성 버튼 클릭
3. 생성된 `data-catalog-topic` 클릭
4. 서브스크립션 탭 클릭 후 서브스크립션 생성 버튼 클릭
      - 기본 설정
            - 이름: `data-catalog-pull-sub`
            - 토픽 선택: `data-catalog-topic`
      - 유형: `Pull`
      - 서브스크립션 메시지 보존 기간: `0일 0시 10분`
      - 응답 대기 시간: `20초`
      - 재처리 횟수: `횟수 지정`, `3번`
      - 생성 버튼 클릭
6. `data-catalog-pull-sub` 서브스크립션의 상태가 `Active`인 것을 확인
![6](https://github.com/user-attachments/assets/53d27a38-a405-4e55-98d4-8ea6750ee6bb)


## 3. 카탈로그 생성(3분)
1. 카카오 클라우드 콘솔 > Analytics > Data Catalog > 카탈로그
2. 카탈로그 생성 버튼 클릭
   - 이름: `data_catalog`
   - VPC 설정
      - VPC: `kc-vpc`
      - 서브넷: `kr-central-2-a의 Public 서브넷`
      - 생성 버튼 클릭
3. `data_catalog` 카탈로그의 상태가 `Running`인 것을 확인
![5](https://github.com/user-attachments/assets/e77c7b14-c637-483f-9ac4-a7227d80b858)


## 4. 데이터베이스 생성(1분)
1. 좌측 데이터베이스 탭 클릭 후 데이터베이스 생성 버튼 클릭  
    - 카탈로그: `data_catalog`  
    - 이름: `data_catalog_database`  
    - 경로  
        - S3 연결: `체크`  
        - 버킷 이름: `data-catalog-bucket`  
        - 디렉터리: `data-catalog-dir`  
    - 설명(선택): 빈칸  
    - 생성 버튼 클릭  
2. `data_catalog_database` 데이터베이스의 상태가 `Active`인 것을 확인  
![4](https://github.com/user-attachments/assets/3c5a51b9-e0b4-4979-8ebd-d961c71a79e0)


## 5. 테이블 생성(1분)
- **Note**: kafka_log_table 테이블 구조
      ![11](https://github.com/user-attachments/assets/a15467e8-a669-4682-a248-4244a32d37ab)

1. 좌측 테이블 탭 클릭 후 테이블 생성 버튼 클릭  
   - 데이터 베이스: `data_catalog_database`  
   - 테이블 이름: `kafka_log_table`  
   - 데이터 저장 경로  
      - S3 연결: `체크`  
      - 버킷 이름: `data-catalog-bucket`  
      - 디렉터리: `kafka-nginx-log/nginx-topic/partition_0/year_{현재 연도}/month_{현재 월}`  
   - 데이터 유형: `JSON`  
   - Pub/Sub 연동: `사용`  
      - 토픽 선택: `data-catalog-topic`  
   - 설명(선택): 빈 칸  
   - 스키마  
      - 필드 추가 버튼 클릭 후 아래 표의 순서대로 스키마 추가
      
        | 파티션 키 | 컬럼 번호 | 필드 이름     | 데이터 유형 |설명(선택)|
        |----------|----------|--------------|------------|------------|
        | 미사용   | 1        | status       | string     | 빈 칸      |
        | 미사용   | 2        | query_params | string     | 빈 칸      |
        | 미사용   | 3        | endpoint     | string     | 빈 칸      |
   - 생성 버튼 클릭
2. `kafka_log_table` 테이블의 상태가 `Active`인 것을 확인
![image](https://github.com/user-attachments/assets/966a8c56-0803-4a5c-935c-330e243b9c35)


## 6. Data Catalog 테이블 이벤트 메시지 수신
1. `traffic-generator-2`에서 Data Catalog 실습용 디렉터리로 이동

      #### lab3-6-1
      
      ```
      cd /home/ubuntu/DataAnalyzeCourse/src/day1/Lab03
      ```

2. 테이블의 이벤트 메시지 확인을 위한 메세지 수신 스크립트 실행
      
      #### lab3-6-2
      
      ```
      python3 data_catalog_subscribe.py
      ```

3. `kafka_log_table` 테이블 클릭
4. 테이블 속성 탭 클릭 후 테이블 속성 추가하기 버튼 클릭
      - Key: `test_key`
      - Value: `test_value`
      - 추가 버튼 클릭
5. `traffic-generator-2` 터미널 창에서 테이블 속성 생성 메시지 정상 수신 로그 확인
![image](https://github.com/user-attachments/assets/d97c438e-702c-43e7-8ede-a3c49655eb64)

6. 스키마 탭 클릭 후 필드 추가 버튼 클릭
      - 컬럼 번호: `4`
      - 필드 이름: `test_field`
      - 데이터 유형: `string`
      - 설명: `Data Catalog 테이블 필드 추가 후 메세지 수신 확인 실습`
      - 생성 버튼 클릭
7. `traffic-generator-2` 터미널 창에서 필드 생성 메시지 정상 수신 로그 확인
![image](https://github.com/user-attachments/assets/a2d2c575-ab4c-439b-b71a-42940a7333d5)


## 7. 크롤러를 통한 MySQL 메타데이터 추출
1. 좌측 크롤러 탭 클릭 후 크롤러 생성 버튼 클릭
    - 데이터베이스: `data_catalog_database`
    - 크롤러 이름: `crawler`
    - MySQL 전체 경로
        - 연결할 MySQL: `database`
        - MySQL 데이터베이스 이름: `shopdb`
    - MySQL 계정
        - ID: `admin`
        - PW: `admin1234`
        - 연결 테스트 버튼 클릭 후 `연결 성공` 확인
    - 설명(선택): 빈 칸
    - 테이블 Prefix(선택): 빈 칸
    - 스케줄: `온디멘드`
    - 생성 버튼 클릭
3. `crawler` 크롤러의 상태가 `Active`인 것을 확인
![9](https://github.com/user-attachments/assets/81b05580-e439-4095-b898-8d6bcfe86b85)

4. 생성된 크롤러 우측의 `⠇` 클릭 후 실행 버튼 클릭
5. 크롤러 실행 모달의 실행 버튼 클릭
6. 크롤러의 상태가 `Active`인 것과 마지막 실행 상태가 `Succeeded`인 것을 확인 
![10](https://github.com/user-attachments/assets/9c471534-bc50-4b73-b1b4-be3c2f217fc0)

7. 좌측 테이블 탭 클릭 후 추출한 MySQL 메타데이터 정보 확인
![11](https://github.com/user-attachments/assets/0a2e267a-6d4b-4a4f-ad47-0d24ed712e40)

