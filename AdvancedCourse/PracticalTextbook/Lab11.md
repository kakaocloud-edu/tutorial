# 리소스 삭제 실습

불필요한 리소스 삭제를 하는 실습입니다.

1. ingress-controller 삭제 (LB 자동 삭제)
     - 접속 중인 Bastion VM 인스턴스에서 아래 명령어 입력
     #### **lab11-1-1**
     ```bash
     kubectl delete -f https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/ingress-nginx-controller.yaml
     ```
2. Virtual Machine > Instance > `bastion VM` 선택 > Instance 삭제 > 영구 삭제 > 삭제 버튼 클릭
3. DNS > DNS Zone > DNS 이름 클릭 > 추가했던 상단 레코드의 오른쪽 (...) 클릭 > 레코드 삭제 클릭 >  오른쪽 상단 레코드의 오른쪽 (...) 클릭 >  DNS 삭제 클릭 > DNS 주소 이름 입력 > 삭제 버튼 클릭
4. Container Registry > Repository > 생성되어 있는 Repository 클릭 > 상단 오른쪽 (...) 클릭 > 리포지토리 삭제 클릭
5. MySQL > Instance Group > 생성되어 있는 인스턴스 그룹 오른쪽 (...) 클릭 > 인스턴스 그룹 삭제 클릭 > 인스턴스 그룹 이름 입력 및 삭제 버튼 클릭
6. Kubernetes Engine > Cluster > 생성되어 있는 클러스터 오른쪽 (...) 클릭 > 클러스터 삭제 클릭
7. VPC > Public IP > 모두 선택 > 삭제 버튼 클릭 > 영구 삭제 입력 > 삭제
8. VPC > 생성되어 있는 VPC 오른쪽 (...) 클릭 > VPC 삭제 > VPC 이름 입력 및 삭제 버튼 클릭
