# Kubernetes Engine 클러스터에 웹서버 자동화 배포하기

지금까지 만든 배포 방식을 자동화하는 도구인 Helm에 대해 실습합니다. Helm을 이용해 Chart를 만들어 배포, 업데이트, 롤백을 진행하는 실습입니다.


## 1. 기존 리소스 삭제

1. yaml 파일 삭제
   - 접속 중인 Bastion VM 인스턴스에 명령어 입력
   #### **lab8-1-1**
   ```bash
   rm -f lab6*.yaml
   ```

2. 실행 중인 리소스 삭제
   #### **lab8-1-2**
   ```bash
   kubectl delete ingress --all
   ```
   
   ```bash
   kubectl delete svc --all
   ```

   ```bash
   kubectl delete deploy --all
   ```

   ```bash
   kubectl delete job sql-job
   ```

   ```bash
   kubectl secret app-secret
   ```
   
   ```bash
   kubectl delete configmap --all
   ```
   ```bash
   kubectl delete po --all
   ```
   

   
3. 실행 중인 리소스가 삭제되었는 지 확인
   #### **lab8-1-3**
   ```bash
   kubectl get ingress
   ```

   ```bash
   kubectl get svc
   ```
   **Note** `service/kubernetes`는 자동 생성되는 리소스로, 재생성되어도 무관합니다.
   
   ```bash
   kubectl get deploy
   ```
   ```bash
   kubectl get po
   ```
   ```bash
   kubectl get job
   ```
   ```bash
   kubectl get configmap
   ```


## 2. Helm Chart 설치


1. Helm Chart 설치
   #### **lab8-2-1**
   ```bash
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

2. 설치 확인
   #### **lab8-2-2**
   ```bash
   helm version
   ```

## 3. Helm Chart 프로젝트 다운 및 확인


1. Helm Chart 프로젝트 다운
   #### **lab8-3-1**
   ```bash
   git clone https://github.com/kakaocloud-edu/tutorial.git
   ```

2. 실습 진행을 위한 디렉터리 이동
   #### **lab8-3-2**
   ```bash
   cd ./tutorial/AdvancedCourse/src/helm
   ```

3. 미리 생성해 놓은 values.yaml 파일 heml 디렉터리로 이동
   #### **lab8-3-3**
   ```bash
   sudo mv /home/ubuntu/values.yaml values.yaml
   ```

## 4. 차트 확인


1. tree 패키지 다운로드
   #### **lab8-4-1**
   ```bash
   sudo apt  install tree
   ```

2. tree를 이용해 차트 확인
   #### **lab8-4-2**
   ```bash
   tree .
   ```

## 5. 차트 문제 검사


1. lint 기능을 이용해 차트에 문제가 있는지 확인
   #### **lab8-5-1**
   ```bash
   helm lint .
   ```

2. 결과 확인
   **Note** `0 chart(s) failed`라고 출력되면 다음 실습을 진행합니다.

## 6. 차트 설치 시뮬레이션 및 차트 설치

   
1. 차트 설치 전 랜더링 테스트

   #### **lab8-6-1**
   ```bash
   helm template . -f values.yaml
   ```

2. 디버그
   #### **lab8-6-2**
   ```bash
   helm install --dry-run --debug my-release . >yamls
   ```

3. 차트 설치
   #### **lab8-6-3**
   ```bash
   helm install my-release . -f values.yaml
   ```

5. 차트 확인

   1. 차트 리스트로 확인
   #### **lab8-6-5**
   ```bash
   helm list
   ```
   **Note** `my-release` 이름으로 차트가 생성되었는지 확인
   

6. 차트 세부 내용 확인
   #### **lab8-6-6**
   ```bash
   helm status my-release   
   ```


## 7. Helm Chart를 이용한 버전 관리

1. replicaCount 수정
   #### **lab8-7-1**
   ```bash
   vi values.yaml
   ```
   - 1라인 : replicaCount : 2
   - `2` -> `3` 수정

2. `helm upgrade`를 통한 차트 릴리즈 업그레이드

   #### **lab8-7-2**
   ```bash
   helm upgrade my-release . --description "#pod 2->3" -f values.yaml
   ```
   
3. 업데이트 확인하기 - CHART REVISION 값 변경 확인
   
   #### **lab8-7-3**
   ```bash
   helm status my-release
   ```

4. 업데이트 확인하기 - Pod 개수 변경 확인
   
   #### **lab8-7-4**
   ```bash
   kubectl get pod
   ```

5. 릴리즈 히스토리 확인
   
   #### **lab8-7-5**
   ```bash
   helm history my-release
   ```

6. 특정 REVISION의 value 값 확인

   #### **lab8-7-6-1**
   ```bash
   helm get values my-release --revision 1
   ```

   #### **lab8-7-6-2**
   ```bash
   helm get values my-release --revision 2
   ```

## 8. 롤백


1. 롤백
   #### **lab8-8-1**
   ```bash
   helm rollback my-release 1
   ```

2. 릴리즈 히스토리 확인
   #### **lab8-8-2**
   ```bash
   helm history my-release
   ```

3. 파드 수 감소 확인
   #### **lab8-8-3**
   ```bash
   kubectl get po
   ```
