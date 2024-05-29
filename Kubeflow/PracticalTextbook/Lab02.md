# Kubeflow 생성
클러스터에 필수 및 선택 노드 풀을 설정하고, Kubeflow 소유자와 DB 설정, Object Storage를 Kubeflow 생성 및 구성하는 실습입니다. 

## Kubeflow 정보
1. 카카오 클라우드 콘솔 > 서비스 > AI Service > Kubeflow > Kubeflow
2. `시작하기` 클릭
3. `Kubeflow 만들기` 클릭
    - Kubeflow 기본 설정 정보
       - Kubeflow 이름 : `kc-handson`
       - 버전 : `1.0.0`
     - 클러스터 연결 : `k8s-cluster`
     - 클러스터 구성
       - Ingress 노드 풀 : `pool-ingress`
       - Worker 노드 풀 : `pool-worker`
       - CPU 노트북 노드 풀 : `pool-worker`
     - 선택 노드풀 설정
       - CPU 노트북 노드 풀 : `pool-worker`
       - CPU 파이프라인 노드 풀 : `pool-worker`
       - GPU 노트북 노드 풀 : `pool-gpu`
       - GPU MIG : `7g 80b`
       - GPU 파이프라인 노드 풀 : `pool-gpu`
     - 디폴트 파일 스토리지 : `handson`
     - Kubeflow 소유자 설정
       - 소유자 이메일 계정 : `입력된 이메일로 임시 비밀번호 발송`
       - 네임 스페이스 이름 : `Kubeflow-tutorial`
       - 디폴트 파일 스토리지 : `handson`
       - DB 설정
         - 포트 : `3306`
         - 비밀번호 : `admin1234!`
       - Object storage 타입 : `KC Object Storage`
       - 도메인 연결 (선택) : (데모)
5. Actove 생성 확인

## Kubeflow 대시보드에 접속하기(로드밸런서 Public IP를 이용)

1. Kubeflow 생성 시 입력한 소유자 이메일 계정, 해당 이메일로 전송된 임시 비밀번호 복사 후 메모장에 붙여넣기
**Note**: 추후 비밀번호 변경 가능
2. 카카오 클라우드 콘솔 > 서비스 > Beyond Networking Service > Load Balancing
3. Kubeflow의 Ingress를 위해 생성된 `kube_service_{프로젝트 아이디}_{IKE 클러스터명}_ingress-nginx_ingress-nginx-controller` 이름의 로드밸런서 확인
4. 이름 오른쪽의 `더보기`(점 3개) 버튼 클릭 
5. `Public IP 연결` 클릭
6. `새로운 Public IP를 생성하고 자동으로 할당` 선택
7. `확인` 클릭
8. 로드밸런서를 이용한 포트포워딩
   - 터미널 열기(윈도우) : Window key + R, "cmd" 입력 후 엔터
     ``` bash
          start http://`LB의 PUBLIC IP`
     ```
     
   - 터미널 열기(Mac) : F4, "터미널" 입력 후 엔터
     ``` bash
          open http://`LB의 PUBLIC IP`
     ```
      
9. 브라우저에서 로드밸런서에 할당된 Public IP 80포트로 접속
9.  `고급` 클릭 > `LB의 PUBLIC IP (안전하지 않음) 클릭`

10. 로그인 진행
    - Email Address : `소유자 이메일 계정`
    - Password : `소유자 이메일로 전송된 초기 패스워드`
11. 로그인 확인
    - **Note**: Kubeflow의 대시보드 창이면 정상 로그인

## Kubeflow 대시보드에 접속하기(Kubectl 포트 포워딩을 이용)

1. 사용자 로컬 시스템의 특정 포트(예:8080)를 Kubeflow 대시보드 포트로 포워딩
   - **Note**: 터미널에 입력
   ```bash
   kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
   ```
3. 브라우저에서 로컬 호스트 8080 포트로 접속
   ```bash
   http://localhost:8080
   ```
4. 로그인 진행
    - Email Address : `소유자 이메일 계정`
    - Password : `소유자 이메일로 전송된 초기 패스워드`
5. 로그인 확인
