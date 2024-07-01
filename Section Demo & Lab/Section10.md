# [Lab] Stored Procedure 설명 및 실습

MySQL의 Stored Procedure(저장 프로시저): SQL 쿼리들을 모아놓은 일종의 함수로, 서버에 저장된 SQL 코드 블록
- 동일한 작업을 반복적으로 수행할 때 효율성을 높임
- 코드 재사용성을 높일 수 있음
- 저장 프로시저는 복잡한 비즈니스 로직을 데이터베이스 내부에서 수행하도록 하여 클라이언트와 서버 간의 통신을 줄이고 성능을 향상시킬 수 있음

1. 데이터베이스 endpoint 주소를 MySQL 콘솔에서 확인
2. CMD 창에서 bastion VM으로 ssh 접속
3. db 접속
    ```bash
    mysql --user=admin --password=admin1234 --host={엔드포인트URL}
    ```
    - 예) mysql --user=admin --password=admin1234 --host=az-a.database.5883f6b1b1914d8d8e44b5026578e0be.mysql.managed-service.kr-central-2.kakaocloud.com
4. db 목록 보기
    ```sql
    show databases;
    ```
5. DB에 정의된 프로시저 목록 확인하기
    ```sql
    show procedure status where db = 'mysql';
    ```
6. mnms_grant_right_user라는 저장 프로시저의 정의 보기
    ```sql
    show create procedure mysql.mnms_grant_right_user;
    ```
7. 사용자(user)와 호스트(host) 정보를 조회하는 SQL 쿼리
    ```sql
    select user, host from mysql.user;
    ```
8. 사용자 생성 프로시저 호출
    ```sql
    call mysql.mnms_create_user('test_user', '%', 'test');
    ```
    - test_user: 새로 생성할 사용자 이름
    - % : 모든 호스트에서 test_user로 접속 가능
    - test: 사용자의 비밀번호
9. 사용자(user)와 호스트(host) 정보를 조회하는 SQL 쿼리
    ```sql
    select user, host from mysql.user;
    ```
10. 생성된 test_user의 권한 확인
    ```sql
    show grants for test_user;
    ```
    - GRANT USAGE ON *.* TO 'test_user'@'%'는 test_user라는 사용자가 MySQL 서버에 접속할 수 있지만, 어떤 데이터베이스나 테이블에 대한 권한은 부여받지 않았다는 것을 나타냄
11. test_user에게 권한 부여
    ```sql
     call mysql.mnms_grant_right_user('test_user', '%', 'ALTER, CREATE, DELETE, DROP, EXECUTE, INSERT, SELECT, UPDATE', '*', '*');
    ```
12. 생성된 test_user의 권한 확인
    ```sql
    show grants for test_user;
    ```
13. 나가기
    ```sql
    exit
    ```
14. test_user로 db 접속
    ```bash
    mysql --user=test_user --password=test --host={엔드포인트URL}
    ```
    - 예) mysql --user=test_user --password=test --host=az-b.database.5883f6b1b1914d8d8e44b5026578e0be.mysql.managed-service.kr-central-2.kakaocloud.com
15. db 생성
    ```sql
    create database user_database;
    ```
16. db 목록 보기
    ```sql
    show databases;
    ```
17. 나가기
    ```sql
    exit
    ```
18. **MySQL 백업 관리 실습을 위해 미리 백업 만들기 진행**
19. admin으로 db 접속
    ```bash
    mysql --user=admin --password=admin1234 --host={엔드포인트URL}
    ```
    - 예) mysql --user=admin --password=admin1234 --host=az-a.database.5883f6b1b1914d8d8e44b5026578e0be.mysql.managed-service.kr-central-2.kakaocloud.com
20. test_user에게 부여했던 권한 모두 회수
    ```sql
    call mysql.mnms_revoke_right_user('test_user', '%', 'ALTER, CREATE, DELETE, DROP, EXECUTE, INSERT, SELECT, UPDATE', '*', '*');
    ```
21. 나가기
    ```sql
    exit
    ```
22. test_user로 db 접속
    ```bash
    mysql --user=test_user --password=test --host={엔드포인트URL}
    ```
    - 예) mysql --user=test_user --password=test --host=az-b.database.5883f6b1b1914d8d8e44b5026578e0be.mysql.managed-service.kr-central-2.kakaocloud.com
23. db 생성 시도 시 불가
    ```sql
    create database user_database;
    ```
24. 나가기
    ```sql
    exit
    ```
25. admin으로 db 접속
    ```sql
    mysql --user=admin --password=admin1234 --host={엔드포인트URL}
    ```
    - 예) mysql --user=admin --password=admin1234 --host=az-a.database.5883f6b1b1914d8d8e44b5026578e0be.mysql.managed-service.kr-central-2.kakaocloud.com
26. 아래의 명령어를 통해 test_user 계정을 삭제
    ```sql
    call mysql.mnms_drop_user('test_user', '%');
    ```
27. 사용자(user)와 호스트(host) 정보를 조회하는 SQL 쿼리
    ```sql
    select user, host from mysql.user;
    ```
