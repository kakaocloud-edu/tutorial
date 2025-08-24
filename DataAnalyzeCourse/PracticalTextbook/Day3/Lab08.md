# Monitoring flow & Alert Center

## 1. Monitering Flow & Alert Center 장애 탐지 (8분)

1. 우측 상단 프로필 이미지 클릭 > 계정 정보
2. 계정 정보 내 이메일 주소 입력
    - **note :** 이메일 인증 필요
3. 카카오 클라우드 콘솔 > Management > Alert Center
4. 좌측 수신 채널 클릭
5. 수신 채널 생성 버튼 클릭
    - 수신 채널 이름 : `mf-email`
    - 메인 채널 유형 : `기본 채널` > `이메일` 선택
    - 수신자 유형
        - `사용자`
        - `{본인의 이메일}` 선택
    - 대체 채널: `미사용` 선택
    - 수신 채널 사용 여부 : `사용` 선택
    - 생성 버튼 클릭
6. 좌측 알림 정책 클릭
7. 알림 정책 생성 클릭
    - 1단계: 알림 조건 설정
        - 조건 유형 : `메트릭`
        - 서비스 : `Monitoring Flow`
        - 조건 설정
            - 메트릭 항목 : `Scenario Fail Count`
            - 리소스: `시나리오`, `lab2`
        - 임계치 : `1` , `count`, `이상`
        - 지속시간 : `1분`
        - 심각도 : `경고`
        - `다음` 버튼 클릭
    - 2단계: 수신 채널 설정
        - 채널 유형 : `이메일`
        - 수신 채널 : `mf-email`
        - `다음` 버튼 클릭
    - 3단계: 기본 정보 설정
        - 알림 정책 이름 : `mf-alert`
        - 알림 정책 설명 (선택) : `빈 칸`
        - 사용 여부 : `기본 체크 상태`
        - `다음` 버튼 클릭
    - 4단계: 검토
        - `설정 정보 확인`
        - `생성` 버튼 클릭
8. 카카오 클라우드 콘솔 > Beyond Compute Service > Virtual Machine
9. `api-server-1` 인스턴스 SSH 접속
    - `api-server-1` 각 인스턴스의 우측 메뉴바 > `SSH 연결` 클릭
    - SSH 접속 명령어 복사
    - 터미널 열기
    - keypair를 다운받아놓은 폴더로 이동 후 터미널에 명령어 붙여넣기 및 **yes** 입력
      
    **lab8-1-9-1**
    ```
    cd {keypair.pem 다운로드 위치}
    ```
        
    - 리눅스의 경우 아래와 같이 키페어 권한 조정
        
    **lab8-1-9-2**
        
    ```
    chmod 400 keypair.pem
    ```
        
    **lab8-1-9-3**
        
    ```
    ssh -i keypair.pem ubuntu@{api-server-1의 public ip 주소}
    ```
    - **Note**: {api-server-1의 public ip 주소} 부분을 복사한 각 IP 주소로 교체
   
10. 장애를 발생시키기 위해 http 80 포트를 2분 동안 차단하는 명령어 실행
    
    **lab8-1-10**

    ```
    sudo nohup bash -c '
      iptables -I INPUT -p tcp --dport 80  -j REJECT
      sleep 120
      iptables -D INPUT -p tcp --dport 80  -j REJECT
    ' >/tmp/http_drop.log 2>&1 &
    ```
    
11. 카카오 클라우드 콘솔 > Management > Monitoring Flow
12. `lab2` 시나리오 클릭
    - 실행 결과 탭 클릭
    - 1분 뒤 새로고침하여 상태가 `Failed` 인 행 확인
    - 다시 1분 뒤 새로고침하여 상태가 `Succeed`로 재전이 되었음을 확인
13. Alert Center 수신 채널에 등록한 이메일로 접속하여 Alert 메일 확인
