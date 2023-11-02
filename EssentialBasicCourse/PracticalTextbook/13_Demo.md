# Alert Center 실습

새로운 알림 정책을 생성합니다. CPU부하기를 통하여 트래픽을 발생 시킵니다. 
발생된 트래픽이 정상적으로 감지되어 설정한 알림 수신 채널로 알림이 오는지 확인하는 실습입니다.

## 1. 연락처 설정 및 수신 채널 생성


1. 우측 상단 프로필 이미지 클릭 > 계정 정보 클릭
2. 계정 정보 내 이메일 주소 및 휴대폰 번호 입력
3. 카카오 클라우드 콘솔 > 전체 서비스 > Alert Center 접속
4. 수신 채널 클릭
5. 수신 채널 만들기 버튼 클릭
    - 수신 채널 이름 : `alert`
    - 채널 유형 : `이메일`, `문자`, `알림톡` 선택
    - 수신자 목록 : `{본인의 이메일}` 선택
    - **Note**: "{본인의 이메일}" 부분을 이메일 주소로 교체하세요.
    - 사용여부 : `사용` 선택
6. 만들기 버튼 클릭

## 2. 메트릭 알림 정책 생성 및 알림 확인
1. 카카오 클라우드 콘솔 > 전체 서비스 > Alert Center 접속
2. 알림 정책 만들기 버튼 클릭
    - 조건 유형 : `메트릭`
    - 서비스 : `Beyond Compute Service`
    - 메트릭 항목 : `CPU Usage`
    - 자원 : `web_server_2`
    - 임계치 : `30%이상`
    - 지속시간 : `1분`
    - 심각도 : `경고`
3. 다음 버튼 클릭
    - 채널 유형 : `이메일`
    - 수신 채널 : `alert`
4. 다음 버튼 클릭
    - 알림 정책 이름 : `CPU_Alert`
5. 다음 버튼 클릭 
6. 만들기 버튼 클릭
7. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
8. Bastion VM의 Public IP 주소 복사
9. Web_server_2의 Private IP 주소 복사
10. 터미널 명령어 입력
    - Keypair를 다운받아놓은 폴더로 이동
    - Bastion을 통해 Web _server_2에 접속
    ```bash
    ssh -i "keyPair.pem" -o ProxyCommand="ssh -W %h:%p centos@{Bastion의 public IP} -i keyPair.pem" centos@{web_server_2의 private IP}
    ```
11. CPU 부하기 패키지 설치 및 부하 생성 및 종료 - 터미널 명령어 입력
    ```bash
    sudo yum install epel-release -y
    ```
    ```bash
    sudo yum install stress -y
    ```
    ```bash
    stress --cpu 2
    ```
    - 1분 후 ctrl+ C 입력
    ```bash 
    crtl + C 
    ```
    
12. 입력했던 이메일 주소에 부하 알림 확인하기

## 3. 이벤트 기반 알림 정책 생성 및 알림 확인


1. 카카오 클라우드 콘솔 > 전체 서비스 > Alert Center 접속
2. 알림 정책 만들기 버튼 클릭
    - 조건 유형 : `이벤트`
    - 서비스 : `Virtual Machine`
    - 이벤트 항목 : `인스턴스 재시작`
3. 다음 버튼 클릭
    - 채널 유형 : `이메일`
    - 수신 채널 : `alert`
4. 다음 버튼 클릭
    - 알림 정책 이름 : `event_Alert`
5. 다음 버튼 클릭
6. 만들기 버튼 클릭
7. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
8. Web_server_2 인스턴스 우측 메뉴바 클릭 > 재시작 버튼 클릭
9. 입력했던 이메일 주소에 이벤트 알림 확인하기

