# [Lab] Redis 설명 및 실습

Data Store는 클라우드 기반 완전 관리형 데이터베이스 서비스 그룹으로 고객의 요구사항에 적합한 데이터베이스 환경을 제공합니다.
카카오클라우드의 Data Store에는 높은 성능과 고가용성을 보장하는 MySQL, Redis 서비스가 포함됩니다.

1. Redis 서버와 상호작용할 수 있는 다양한 유틸리티가 포함된 redis-tools 패키지 설치
    ```bash
    sudo apt install redis-tools -y
    ```
2. 인스턴스를 클러스터에 연결
    ```bash
    redis-cli -h {복사해둔-Rediscluster-ENDPOINT} -p 6379 hello
    ```
    - "server": "redis" - 서버의 종류를 나타냅니다. 여기서는 Redis 서버임을 나타냅니다.
    - "version": "6.2.5" - Redis 서버의 버전입니다.
    - "proto": 2 - 클라이언트와 서버 간에 사용되는 프로토콜 버전입니다.
    - "id": 56 - 클라이언트의 고유 식별자입니다.
    - "mode": "standalone" - 서버의 운영 모드입니다. 여기서는 단일 서버 모드(standalone)임을 나타냅니다.
    - "role": "master" - 서버의 역할입니다. 여기서는 마스터 역할을 하고 있음을 나타냅니다.
    - "modules" - 현재 로드된 모듈입니다. 이 경우 빈 리스트로 표시되어 있으며, 로드된 모듈이 없음을 의미합니다.
3. 데이터 저장 (SET 명령어)
    ```bash
    redis-cli –h {복사해둔-Rediscluster-ENDPOINT} –p 6379 SET mykey “Hello, Redis!”
    ```
4. 데이터 조회 (GET 명령어)
    ```bash
    redis-cli –h {복사해둔-Rediscluster-ENDPOINT} –p 6379 GET mykey
    ```
