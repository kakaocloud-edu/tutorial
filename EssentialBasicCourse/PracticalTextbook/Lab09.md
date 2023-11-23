# File Storage 실습

새로운 File Storage 인스턴스를 생성합니다. File Storage를 사용중인 VM인스턴스와 연결 후 연결된 File Storage를 마운트 해제하는 실습입니다.

## 1. File Storage 인스턴스 생성하기


1. 카카오 클라우드 콘솔 > 전체 서비스 > File Storage 접속
2. 우측 상단 Instance 만들기 버튼 클릭
     - Instance 이름 : `fs-01`
     - Volume 크기 : `1 TB`
     - Network 설정 : 
          - VPC: `vpc1`
          - Subnet: `main`
     - 마운트 정보 설정 : `fileshare-01`
3. 만들기 버튼 클릭

## 2. Bastion VM에서 마운트하기


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virual Machine 접속
2. 생성된 인스턴스의 우측 메뉴바 > SSH 연결 클릭
     - SSH 접속 명령어 복사(다운받은 keyPair.pem 파일이 있는 경로에서 아래 명령어를 실행합니다.)
     - 터미널 열기
     - Keypair를 다운받아놓은 폴더로 이동
     - 터미널에 명령어 붙여넣기
     - yes 입력
       
     #### **lab9-2-2-1**
     ```bash
     cd {keyPair.pem 다운로드 위치}
     ```
     
     #### **lab9-2-2-2**
     ```bash
     ssh -i keyPair.pem centos@{bastion의 public ip주소}
     ```
     - **Note**: "bastion의 public ip주소" 부분을 복사한 IP 주소로 교체하세요.

3. NFS 패키지 설치 - 터미널 명령어 입력
       
     #### **lab9-2-3-1**
     ```bash
     sudo yum install -y nfs-utils
     ```
     
     #### **lab9-2-3-2**
     ```bash 
     mkdir fs1
     ```
      
     #### **lab9-2-3-3**
     ```bash
     ls -al
     ```
4. 카카오 클라우드 콘솔 > 전체 서비스 > file Storage 접속
5. fs-01 인스턴스의 마운트 정보 복사 버튼 클릭
6. VM에서 마운트하기 - 터미널 명령어 붙여넣기 
      
     #### **lab9-2-6**
     ```bash
     #마운트 정보 복사 내용 붙여넣기
     sudo mount -t nfs {File Storage 인스턴스 사설 IP}:/{파일 공유 이름} fs1
     ```
     - **Note**: "{File Storage 인스턴스 사설 IP}:/{파일 공유 이름}" 부분을 마운트 정보 복사본으로 교체하세요.
7. NFS마운트 여부 확인 
      
     #### **lab9-2-7**
     ```bash
     mount
     ```
8. 마운트 된 디렉터리 권한 변경하기 - 터미널 명령어 입력 
      
     #### **lab9-2-8**
     ```bash
     sudo chmod 777 fs1
     ```
9. 변경된 권한 확인하기 
      
     #### **lab9-2-9**
     ```bash
     ls -l
     ```

## 3. 예제를 통한 File Storage 실습


1. 테스트 파일 생성 - 터미널 명령어 입력 
      
     #### **lab9-3-1-1**
     ```bash
     cd fs1
     ``` 
      
     #### **lab9-3-1-2**
     ```bash
     cat > test.txt
     ``` 
      
     #### **lab9-3-1-3**
     ```bash
     I am a test file
     ```
     - UNIX 계열 시스템에서는 Ctrl+D (파일의 끝을 나타냄), Windows에서는 Ctrl+Z 를 눌러서 입력을 종료
2. 테스트 파일 확인 - 터미널 명령어 입력 
      
     #### **lab9-3-2**
     ```bash
     cat test.txt
     ```

3. web_server_1 VM 접속
     - 카카오 클라우드 콘솔 > 전체 서비스 > Virual Machine 접속
     - Virtual Machine > Instance 
     - Bastion VM과  Web Server의 IP 확인하기
     - Bastion의 `Public IP 주소` 확인 및 복사
     - Web_server_1의 `Private IP 주소` 확인 및 복사

      
     #### **lab9-3-5-1**
     ```bash
     cd {keyPair.pem 다운로드 위치}
     ```
     - **Note**: "{keyPair.pem 다운로드 위치}" 부분을 keyPair.pem의 디렉터리 위치로 교체하세요. 
      
     #### **lab9-3-5-2**
     ```bash
     ssh -i "keyPair.pem" -o ProxyCommand="ssh -W %h:%p centos@{bastion의 public IP} -i keyPair.pem" centos@{web_server_1의 private IP}
     ```
     - **Note**: "{Bastion의 public IP}", "{web_server_1의 private IP}" 부분을 복사한 IP 주소로 교체하세요.

     #### **lab9-3-5-3**
     ```bash
     yes
     ```

4. web_server_1 VM에 NFS 패키지 설치 - 터미널 명령어 입력 
      
     #### **lab9-3-6-1**
     ```bash
     sudo yum install -y nfs-utils
     ``` 
      
     #### **lab9-3-6-2**
     ```bash 
     mkdir fs2
     ``` 
      
     #### **lab9-3-6-3**
     ```bash
     ls -l
     ```
5. 카카오 클라우드 콘솔 > 전체 서비스 > file Storage 접속
6. fs-01 인스턴스의 마운트 정보 복사 버튼 클릭
7. web_server_1 VM에서 마운트하기 - 터미널 명령어 붙여넣기 
      
     #### **lab9-3-9**
     ```bash
     #마운트 정보 복사 내용 붙여넣기
     sudo mount -t nfs {File Storage 인스턴스 사설 IP}:/{파일 공유 이름} fs2
     ```
     - **Note**: "{File Storage 인스턴스 사설 IP}:/{파일 공유 이름}" 부분을 마운트 정보 복사본으로 교체하세요.
10. NFS마운트 여부 확인 
      
     #### **lab9-3-10**
     ```bash
     mount
     ```
11. 디렉터리 이동 및 테스트 파일 확인 - 터미널 명령어 입력 
      
     #### **lab9-3-11-1**
     ```bash
     cd fs2
     ``` 
      
     #### **lab9-3-11-2**
     ```bash
     ls -l
     ```
12. 테스트 파일 확인 - 터미널 명령어 입력 
      
     #### **lab9-3-12**
     ```bash
     cat test.txt
     ```
13. NFS 마운트 해제하기 - 터미널 명령어 입력 
      
     #### **lab9-3-13-1**
     ```bash
     cd ~
     ``` 
      
     #### **lab9-3-13-2**
     ```bash
     sudo umount fs2
     ```
14. NFS 마운트 상태 확인하기 - 터미널 명령어 입력 
      
     #### **lab9-3-14**
     ```bash
     mount
     ```
