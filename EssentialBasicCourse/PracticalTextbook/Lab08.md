# TGW 구성 실습

새로운 VPC2를 생성하고 VPC2에 VM을 생성합니다. 
VPC1과 VPC2를 연결하는 TGW를 생성하고 설정합니다. TGW를 통해 서로 다른 VPC간 통신이 가능한지 확인하는 실습입니다.

```mermaid
graph LR
    시작(시작) --> VPC2생성(VPC2 생성)
    VPC2생성 --> VPC2내VM생성(VPC2내 VM 인스턴스 생성)
    VPC2내VM생성 --> TGW생성(TGW 생성)

    subgraph TGW 및 라우팅 설정
        TGW생성 --> VPC1TGW연결(VPC1 TGW Attachment)
        VPC1TGW연결 --> VPC2TGW연결(VPC2 TGW Attachment)
        VPC2TGW연결 --> TGWRoute설정(TGW Route 설정)
        TGWRoute설정 --> VPC1Route설정(VPC1 Route 설정)
        VPC1Route설정 --> VPC2Route설정(VPC2 Route 설정)
    end

    VPC2Route설정 --> VPC간통신확인(VPC간 통신 확인)
    VPC간통신확인 --> 종료(종료)

    %% 강조
    class VPC2생성,VPC2내VM생성,TGW생성,VPC간통신확인 emphasized;
    
    %% 클래스 스타일
    classDef emphasized fill:#f9f,stroke:#333,stroke-width:4px;

```


## 1. VPC2 생성


1. 카카오 클라우드 콘솔 > 전체 서비스 > VPC 접속
2. VPC 만들기 버튼 클릭
     - VPC 이름 : `vpc_2`
     - VPC IP CIDR 블록 : `172.31.0.0/16`
     - AZ 개수 : `1`
     - 첫 번째 AZ : `kr-central-2-a`
     - AZ당 Public Subnet 개수 : `1`
     - AZ당 Private Subnet 개수 : `0`
     - Public Subnet IPv4 CIDR 블록 : `172.31.0.0/20`
     ![image](https://github.com/kakaocloud-edu/tutorial/assets/128004136/5a109ae3-5813-44a8-a336-4820e639d084)
3. 만들기 버튼 클릭
   


## 2. VPC2내 VM 인스턴스 생성


1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine 접속
2. bastion 인스턴스의 Private IP 주소 복사
3. Instance 만들기 버튼 클릭
     - 이름 : `vpc2_vm`
     - Image : `CentOS Stream 8 - 4.18.0-516`
     - Instance 타입 : `m2a.large`
     - Key Pair : `keyPair`
     - VPC : `vpc_2`
     - Subnet : `main`
4. 새 SecurityGroup 생성 클릭
     - Security Group 이름 : `vpc2_vm`
     - Inbound 
          - 프로토콜: `ICMP`, 패킷 출발지: `{bastion VM의 Private IP/32}`
               - **Note**: "bastion VM의 Private IP/32" 부분을 bastion VM의 Private IP 주소로 교체하세요.
     - Outbound 
          - 프로토콜: `ALL`, 패킷 출발지: `0.0.0.0/0`
5. bastion 인스턴스의 우측 메뉴바 클릭 > Public IP 연결 클릭
     - `새로운 Public IP를 생성하고 자동으로 할당` 선택
6. 확인 버튼 클릭    

 ## 3-1. TGW 생성 및 설정


1. 전체 서비스 > Transit Gateway 만들기 클릭 
2. Transit Gateway 만들기 클릭 
     - 이름 : `transit`
     - 기본 연결 : `연결`
3. 만들기 버튼 클릭
4. 전체 서비스 > Transit Gateway
5. 생성된 transit의 우측 메뉴바 클릭 > Attachment 추가 클릭
     - VPC : `vpc_2`
     - Subnet : `main (kr-central-2-a만 설정)`
6. 적용 버튼 클릭
7. 전체 서비스 > Transit Gateway
8. transit의 우측 메뉴바 클릭 > Attachment 추가 클릭
     - VPC : `vpc_1`
     - Subnet : `main (kr-central-2-a만 설정)`
9. 적용 버튼 클릭
10. 전체 서비스 > Transit Gateway
11. Route Table > transit-route-table 클릭
12. Route 클릭
13. static Route 추가 버튼 클릭
     - 목적지 : `172.31.0.0/16`(vpc_2의 IP CIDR블록)
     - Target : `vpc_2 선택` 
14. 추가 버튼 클릭
15. static Route 추가 버튼 클릭
     - 목적지 : `172.30.0.0/16`(vpc_1의 IP CIDR블록)
     - Target : `vpc_1 선택` 
## 3-2. VPC의 라우트 설정
1. 카카오 클라우드 콘솔 > 전체 서비스 > VPC
2. Route Table 탭 > vpc_1의 main 클릭
3. Route 추가 버튼 클릭
     - Route 추가 클릭
     - Target 타입 : `Transit Gateway`
     - 목적지 : `172.31.0.0/16`(vpc_2의 IP CIDR 블록)
4. 카카오 클라우드 콘솔 > 전체 서비스 > VPC
5. Route Table 탭 > vpc_2의 main 클릭
6. Route 추가 버튼 클릭
     - Route 추가 클릭
     - Target 타입 : `Transit Gateway`
     - 목적지 : `172.30.0.0/16`(vpc_1의 IP CIDR 블록)

## 4. VPC간 통신 확인
1. 카카오 클라우드 콘솔 > 전체 서비스 > Virtual Machine > Instance
2. Bastion VM의 Public IP 주소 복사
3. vpc2_vm의  Private IP 주소 복사
4. 명령어 입력
     - Keypair을 다운받아놓은 폴더로 이동
     - Bastion VM에 접속
     - ping 명령어를 통해 vpc_2에 있는 vm에 패킷이 전달됨을 확인
     - vpc_1 -> vpc_2의 통신이 가능함을 알 수 있음
           
     #### **lab8-4-4-1**
     ```bash
     ssh -i keyPair.pem centos@{bastion의 Public IP}
     ```
     - **Note**: "bastion의 Public IP" 부분을 bastion의 Public IP 주소로 변경하세요.
        
     #### **lab8-4-4-2**
     ```bash 
     ping `{vpc2-vm의 Private IP}`
     ```
