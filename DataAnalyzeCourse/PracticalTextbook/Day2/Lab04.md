# hadoop eco의 hive로 테이블 생성 및 hue 쿼리

hadoop eco의 hive를 활용하여 nginx 로그 데이터와 mysql 데이터를 external table로 생성합니다. 생성된 테이블을 이용하여 hue로 쿼리를 진행하는 실습입니다.

---
## 1. 생성한 hadoop-eco 마스터 노드에 접속

1. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
2. `HadoopMST-core-hadoop-1` 상태 Actice 확인 후 인스턴스의 우측 메뉴바 > `Public IP 연결` 클릭

    - `새로운 퍼블릭 IP를 생성하고 자동으로 할당`
    - 확인 버튼 클릭

3. `HadoopMST-core-hadoop-1` 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭

    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동
    - 터미널에 명령어 붙여넣기
    - yes 입력

    #### **lab4-1-3-1**
    
    ```bash
    cd {keypair.pem 다운로드 위치}
    ```
    
    - 리눅스의 경우에 아래와 같이 키페어의 권한을 조정
    
    #### **lab4-1-3-2**
    
    ```bash
    chmod 400 keypair.pem
    ```
    
    #### **lab4-1-3-3**
    
    ```bash
    ssh -i keypair.pem ubuntu@{HadoopMST-core-hadoop-1 public ip주소}
    ```
    
    
    
    #### **lab4-1-3-4**
    
    ```bash
    yes
    ```

## 2. hive에 external table 생성


