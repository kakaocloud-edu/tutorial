# VPC 생성(Demo로 진행)

VPC 생성 방법 및 서브넷 설정에 대한 실습입니다.

![image](https://github.com/user-attachments/assets/37ab57cb-49d4-4100-824b-f86be1b12056)


## 1. VPC 생성


1. 카카오 클라우드 콘솔 > 전체 서비스 > VPC 접속
2. VPC 만들기 버튼 클릭
     - VPC 정보
          - VPC 이름 : `vpc_1`
          - VPC IP CIDR 블록 : `172.30.0.0/16`
     - Availability Zone
          - AZ 개수 : `1`
          - 첫 번째 AZ : `kr-central-2-a`
     - Subnet 설정
          - AZ당 Public Subnet 개수 : `1`
          - AZ당 Private Subnet 개수 : `1`
          - kr-central2-a의 Public Subnet IPv4 CIDR 블록 : `172.30.0.0/20`
          - kr-central2-a의 Private Subnet IPv4 CIDR 블록 : `172.30.16.0/20`
3. 만들기 버튼 클릭
