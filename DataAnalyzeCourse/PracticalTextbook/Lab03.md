# Data Catalog 실습

## 1. 카탈로그 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Catalog > 카탈로그
2. `카탈로그 생성` 클릭

   - 이름: `data_catalog`
   - VPC 설정
      - VPC: `kc-vpc`
      - 서브넷: `kr-central-2-a의 Public 서브넷`

3. 생성 버튼 클릭


## 2. 연결할 Object Storage 버킷 퍼블릭 액세스 허용
1. 카카오 클라우드 콘솔 > 전체 서비스 > Object Storage

   - `kafka-nginx-log` 클릭
   - `권한` 클릭
   - `접근` 클릭
      - `접근 설정` 클릭
         - `퍼블릭 액세스 허용 (Read Only) 클릭
2. 저장 버튼 클릭


## 3. 데이터베이스 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Catalog > 데이터베이스
2. 데이터베이스 생성 클릭
   
   - 카탈로그: `data_catalog`
   - 이름: `dc_database`
   - 경로
      - S3 연결: `체크`
      - 버킷 이름: `kafka-nginx-log`(카프카와 연동된 버킷)
      - 디렉터리: `nginx-log/CustomTopicDir/MyPartition_0`// 경로 수정한 부분
3. 생성 버튼 클릭


## 4. 테이블 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Data Catalog > 테이블
2. `테이블 생성` 클릭
- **kafka_data** 테이블
   - 데이터 베이스: `dc_database`
   - 테이블 이름: `kafka_data`
   - 테이블 저장 경로
      - S3 연결: `체크`
      - 버킷 이름: `kafka-nginx-log`(카프카와 연동된 버킷)
      - 디렉터리: `nginx-log/CustomTopicDir/MyPartition_0` // 경로 수정한 부분
   - 데이터 유형: `JSON`
   - Pub/Sub 연동: `사용`
      - 토픽 선택: `data-catalog-topic`
   - 설명(선택): `없음`
   - 스키마
      - `필드추가` 클릭
      - 필드 정보
      - **Note**: `파티션 키`는 `partition` 불가능, Hadoop 연동시 문제
         - `파티션 키`: 사용
         - 필드 이름: `partition_key`
         - 데이터 유형: `string`
         - ---
    
         - `파티션 키`: 미사용
         - 필드 이름: `request`, `method`, `session_id`, `endpoint`, `http_referer`, `query_params`, `status`, `timestamp`
         - 데이터 유형: `string`
         - ---
3. 생성 버튼 클릭


## 5. 메시지 확인 실습
1. pub/sub 연동을 통한 메시지 확인


   ### Traffic Generator VM2에서 메시지 확인 코드 실행
   - 기존에 쓰던 `restapi_pull_sub.py`에서 subscription 이름만 `data-catalog-pull-sub`로 변경
   - [`restapi_pull_sub.py`](https://github.com/kakaocloud-edu/tutorial/blob/main/DataAnalyzeCourse/src/TrafficGenerator/REST_API/VM2/restapi_pull_sub.py)


   ```
   def main():
    # Pull Subscription 이름 설정
    subscription_name = data-catalog-pull-sub
   ```

2. 콘솔에서 이벤트 발생
   - 데이터 속성 추가
   - 스키마 필드 추가
   - 스키마 필드 삭제
     
3. Traffic Generator VM2의 터미널 창에서 실시간 메시지 수신 확인

   
## 6. Hadoop 연동을 통한 메시지 확인
### Hadoop 생성
1. 카카오 클라우드 콘솔 > 전체 서비스 > Hadoop Eco
2. 클러스터 생성 클릭

   - 클러스터 이름: `core-hadoop-cluster`
   - 클러스터 구성
        - 클러스터 버전: `Hadoop Eco 2.1.0`
        - 클러스터 유형: `Core-Hadoop`
        - 클러스터 가용성: `미체크`
   - 관리자 설정
        - 관리자 아이디: `admin`
        - 관리자 비밀번호: `Admin1234!`
        - 관리자 비밀번호 확인: `Admin1234!`
   - VPC 설정
        - VPC: `kc-vpc`
        - 서브넷: `kr-central-2-a의 Public 서브넷`
   - 보안 그룹 설정
        - 보안 그룹 설정: `새 보안 그룹 생성`
        - 보안 그룹 이름: `HDE-210-hadoop` {기본 입력 정보 사용}
   - 다음 버튼 클릭
   - 마스터 노드 설정
        - 마스터 노드 인스턴스 개수: `1`
        - 마스터 노드 인스턴스 유형: `m2a.xlarge`
        - 디스크 볼륨 유형 / 크기: `50`
   - 워커 노드 설정
        - 워커 노드 인스턴스 개수: `2`
        - 마스터 노드 인스턴스 유형: `m2a.xlarge`
        - 디스크 볼륨 유형 / 크기: `100`
   - 총 YARN 사용량
        - YARN Core: `6개` {입력 필요X}
        - YARN Memory: `20GB` {입력 필요X}
   - 키 페어: `{기존 생성 키 페어}`
   - 사용자 스크립트(선택): `없음`
   - 다음 버튼 클릭

   - 모니터링 에이전트 설치: `설치 안함`
   - 서비스 연동: `Data Catalog 연동`
        - 카탈로그 이름: `data_catalog`
   - HDFS 설정
        - HDFS 블록 크기: `128`
        - HDFS 복제 개수: `2`
   - 클러스터 구성 설정(선택): `{아래 코드 입력}`
      ```
         {
         "configurations": [
             {
             "classification": "core-site",
             "properties": {
                 "fs.swifta.service.kic.credential.id": "${ACCESS_KEY}",
                 "fs.swifta.service.kic.credential.secret": "${ACCESS_SECRET_KEY}"
             }
             }
         ]
         }
        ```
   - Kerberos 설치: `설치 안함`
   - Ranger 설치: `설치 안함`
3. 생성 버튼 클릭
4. Hadoop Eco 클러스터 생성 확인
5. 마스터/워커 노드 VM 생성 확인
      - 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > 인스턴스

      - **Note**: 보안 그룹 22번 포트 열기
   
   5-1. 마스터 노드 VM(HadoopMST) 옆의 `...` 클릭 후 `보안 그룹 수정` 클릭
   
   5-2. `보안 그룹 선택` 클릭
   
   5-3. `보안 그룹 생성` 버튼 클릭
   
      - 보안 그룹 이름: `hadoop_mst`
      - 보안 그룹 설명: `없음`
      - 인바운드 규칙
        - 프로토콜: `TCP`, 출발지: `0.0.0.0/0`, 포트 번호: `22`
      - 아웃바운드 규칙
        - 프로토콜: `ALL`, 출발지: `0.0.0.0/0`, 포트 번호: `ALL`
      - 생성 버튼 클릭
  
   5-4. 적용 버튼 클릭

7. 마스터 노드에 public IP 부여 후 ssh 접속
   
   - 마스터 노드 VM(HadoopMST)에 SSH로 접속
   
   #### **lab3-1-1**

   ```bash
   ssh -i {keypair}.pem ubuntu@{vm public ip}
   ```
   
8. Hadoop 설정

   - core-site.xml 설정 변경

   #### **lab3-1-2**
   ```
   cd /etc/hadoop/conf
   sudo vi core-site.xml
   ```

   - 아래 값으로 변경 

   ```
   <property>
      <name>fs.s3a.endpoint</name>
      <value>objectstorage.kr-central-2.kakaocloud.com</value>
   </property>
   <property>
      <name>s3service.s3-endpoint</name>
      <value>objectstorage.kr-central-2.kakaocloud.com</value>
   </property>
   ```
   
9. Hive 실행
   #### **lab3-1-3**
   ```
   hive
   ```

10. 사용할 데이터 베이스 선택
    #### **lab3-1-4** 
    ```
    use {database 이름};
    ```

11. 테이블에 파티션 추가

    - **Note**: 사용하는 모든 테이블의 파티션을 추가해줘야함!!

    #### **lab3-1-5**
    ```
    ALTER TABLE {테이블 이름}
    ADD PARTITION (partition_key='0')
    LOCATION 's3a://{Object Storage 경로}';
    ```
    
    - 예시
    ```
    ALTER TABLE alb_data
    ADD PARTITION (partition_key='0')
    LOCATION 's3a://alb-logs/KCLogs/kr-central-2/2025'
    ```
   
12. 테이블 파이션 키 삭제
    #### **lab3-1-6**
    ```
    ALTER TABLE part_test_lsh DROP PARTITION (partition_key='0');
    ```
   

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
        - 연결 테스트 버튼 클릭(연결 테스트 완료 후에 생성 가능)
    - 설명 (선택): `없음`
    - 테이블 Prefix (선택): `없음`
    - 스케줄: `온디멘드`
3. 생성 버튼 클릭
4. 생성된 크롤러 선택 후 실행
5. 카카오 클라우드 콘솔 > 전체 서비스 > Data catalog > 테이블
      - 생성된 테이블 확인

