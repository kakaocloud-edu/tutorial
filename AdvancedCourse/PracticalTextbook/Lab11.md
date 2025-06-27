# 리소스 삭제 실습

실습을 진행하면 만들어진 리소스를 삭제를 하는 실습입니다.

## 1. 쿠버네티스 리소스 삭제
   1. Helm 차트를 통해 설치한 Kubernetes 애플리케이션 삭제
   #### **lab11-1**
   ```bash
   helm uninstall my-release
   ```
   2. Helm 차트를 통해 설치한 Kubernetes 클러스터의 Metrics Server 삭제
   #### **lab11-2**
   ```bash
   helm uninstall metrics-server
   ```
   3. ingress-controller 삭제 (LB 자동 삭제)
   - 접속 중인 Bastion VM 인스턴스에서 아래 명령어 입력
   #### **lab11-3**
   ```bash
   kubectl delete -f https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/ingress-nginx-controller.yaml
   ```
   
   4. 리소스 삭제 확인
   #### **lab11-4**
   ```bash
   kubectl get all  --all-namespaces
   ```
<br>

## 2. 기타 클라우드 리소스들 삭제
1. Virtual Machine > Instance > `bastion VM` 선택 > Instance 삭제 > 영구 삭제 > 삭제 버튼 클릭
2.  Virtual Machine > 키 페어 > 생성된 키의 오른쪽 (...) 클릭 > 키 페어 삭제
3. DNS > DNS Zone > DNS 이름 클릭 > 추가했던 상단 레코드의 오른쪽 (...) 클릭 > 레코드 삭제 클릭 >  오른쪽 상단 레코드의 오른쪽 (...) 클릭 >  DNS 삭제 클릭 > DNS 주소 이름 입력 > 삭제 버튼 클릭
4. Container Registry > Repository > 생성되어 있는 Repository 클릭 > 상단 오른쪽 (...) 클릭 > 리포지토리 삭제 클릭
5. MySQL > Instance Group > 생성되어 있는 인스턴스 그룹 오른쪽 (...) 클릭 > 인스턴스 그룹 삭제 클릭 > 인스턴스 그룹 이름 입력 및 삭제 버튼 클릭
6. Kubernetes Engine > Cluster > 생성되어 있는 클러스터 오른쪽 (...) 클릭 > 클러스터 삭제 클릭
7. VPC > Public IP > 모두 선택 > 삭제 버튼 클릭 > 영구 삭제 입력 > 삭제
8. VPC > 생성되어 있는 VPC 오른쪽 (...) 클릭 > VPC 삭제 > VPC 이름 입력 및 삭제 버튼 클릭
9. VPC > 보안 그룹 > bastion 보안그룹 선택 > 생성된 보안 그룹의 오른쪽 (...) 클릭 > 보안 그룹 삭제 클릭
10. 오른쪽 상단의 아이콘 클릭 > 자격 증명 클릭 > 생성된 액세스 키의 오른쪽 (...) 클릭 > 삭제 클릭
