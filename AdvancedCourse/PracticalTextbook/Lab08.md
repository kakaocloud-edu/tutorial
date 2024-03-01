# Kubernetes Engine 클러스터에 웹서버 자동화 배포하기

지금까지 만든 배포 방식을 자동화하는 도구인 Helm에 대해 실습합니다. Helm을 이용해 Chart를 만들어 배포, 업데이트, 롤백을 진행하는 실습입니다.


## 1. 기존 리소스 삭제


1. YAML 파일 삭제
   #### **lab8-1-1**
   ```bash
   rm -f lab6-manifests.yaml
   ```

2. 실행 중인 리소스 삭제
   #### **lab8-1-2**
   ```bash
   kubectl delete ingress --all
   kubectl delete svc --all
   kubectl delete deploy --all
   kubectl delete job sql-job
   kubectl delete secret app-secret
   kubectl delete configmap --all
   ```

2. 실행 중인 리소스가 삭제되었는 지 확인
   #### **lab8-1-3**
   ```bash
   kubectl get ingress
   ```
   ```bash
   kubectl get svc
   ```
   **Note**: `service/kubernetes`는 쿠버네티스 클러스터 내에서 API 서버의 기본 서비스를 나타냄
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
   **Note**: `kube-root-ca.crt`는 쿠버네티스 클러스터에서 사용되는 루트 인증서(root certificate) 파일
   ```bash
   kubectl get secret
   ```
   **Note**: `default-token-*****`는 쿠버네티스 클러스터 내의 서비스 어카운트 토큰(Secret)을 나타냄

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

## 3. Helm Chart 프로젝트 설정


1. 실습 진행을 위한 디렉터리 이동
   #### **lab8-3-1**
   ```bash
   cd /home/ubuntu/tutorial/AdvancedCourse/src/helm
   ```

2. 미리 생성해 놓은 values.yaml 파일 heml 디렉터리로 이동
   #### **lab8-3-2**
   ```bash
   sudo mv /home/ubuntu/values.yaml values.yaml
   ```

## 4. 차트 확인
1. tree를 이용해 차트 확인
   #### **lab8-4-1**
   ```bash
   tree .
   ```

## 5. 차트 문제 검사


1. lint 기능을 이용해 차트에 문제가 있는지 확인
   #### **lab8-5-1**
   ```bash
   helm lint .
   ```

## 6. 차트 설치 시뮬레이션 및 차트 설치

   
1. 차트 설치 전 랜더링 테스트

   #### **lab8-6-1**
   ```bash
   helm template . -f values.yaml
   ```

2. 디버그
   #### **lab8-6-2**
   ```bash
   sudo helm install --dry-run --debug my-release . | tee ~/yamls
   ```

3. 차트 설치
   #### **lab8-6-3**
   ```bash
   helm install my-release . -f values.yaml
   ```

4. 차트 확인

   #### **lab8-6-4**
   ```bash
   helm list
   ```
   - **Note** `my-release` 이름으로 차트가 생성되었는지 확인
   

5. 차트 세부 내용 확인
   #### **lab8-6-5**
   ```bash
   helm status my-release   
   ```


6. 파드 상태 확인
   #### **lab8-6-6**
   ```bash
   kubectl get all  
   ```

7. 웹 사이트 배포 확인
- **Note** my-release-kc-spring-demo-... 이름으로 서버 호스트 이름이 변경되었는지 확인

## 7. Helm Chart를 이용한 버전 관리

1. replicaCount 수정
   #### **lab8-7-1**
   ```bash
   sudo vi values.yaml
   ```
   - 1라인 : replicaCount : 2
   - `2` -> `3` 수정
   - ESC 버튼 + :wq + Enter 버튼 입력으로 저장 후 나가기

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
