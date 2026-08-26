# Kubeflow 모델 서빙 API 생성
카카오클라우드의 Kubeflow 환경에서 KServe를 이용하여 모델 서빙 API를 구축하고 API를 테스트해보는 실습입니다. 

## 1. 사전 작업

### 1. 로드밸런서 IP 와 준비된 도메인 주소 연결
1. 카카오 클라우드 콘솔 > Beyond Networking Service > DNS > DNS Zone
2. DNS Zone 탭 > `DNS Zone 만들기` 버튼 클릭
3.  DNS Zone 생성
    - DNS Zone 설정 정보
        - DNS Zone 이름: kakaocloud-edu.com 입력
        - DNS Zone 설명(선택) : 빈칸
    - `만들기` 버튼 클릭
4. 생성된 `DNS(kakaocloud-edu.com)` 클릭
5. `레코드 추가` 버튼 클릭
6. 레코드 추가 설정 값 입력
    - 레코드 타입: `A`
    - 레코드 이름: 빈칸
    - TTL(초): `300`
    - 값: `LB의 퍼블릭 IP 입력`
    - `추가` 버튼 클릭
7. 웹 브라우저를 통한 접속 확인
    - 주소 창에 `kakaocloud-edu.com` 입력
    - 접속 확인

### 2. Serving 환경 준비
1. Lab 2-1 Kubeflow 생성 시 도메인 연결(선택) 항목에 도메인 설정 필요
    - 도메인 입력 완료된 Kubeflow 사용
2. Lab 3-1 네임스페이스 쿼터 설정 시 원활한 실습이 어려울 수 있으므로, ‘쿼터 미 설정’ 된 사용자로 실습 진행
3. 기존에 사용하던 CPU 이미지 기반의 노트북(cpu-notebook) 사용

## 2. 노트북에서 모델 학습 및 서빙 API 생성 파이프라인 만들기
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 버튼 클릭
2. Other 중 Terminal 클릭
3. `fmnist-kserve.ipynb` 파일 다운로드
    - 아래 명령어 입력
    #### **lab2-3-2**
    ```bash
    wget -O fmnist-kserve.ipynb "https://objectstorage.kr-central-2.kakaocloud.com/v1/32ac749f528f41958493b28d9387911c/kubeflow/fmnist-kserve_v3_cpu.ipynb"
    ```
    - `fmnist-kserve.ipynb` 파일 생성 확인
4. 라이브러리 추가 및 데이터 확인
  - **Note**: Fashion MNIST 데이터셋 다운로드 및 시각화
    - fmnist-kserve.ipynb 파일 더블클릭
    - 1번 스크립트 클릭 후 `RUN` 클릭
    - 이미지 그리드 확인
5. 환경 변수 설정
    - 아래 환경 변수들에 값들을 넣어주세요.
      - KUBEFLOW_HOST : {도메인 주소} 입력
      - KUBEFLOW_USERNAME : {계정 아이디(이메일)} 입력
      - KUBEFLOW_PASSWORD : {계정 비밀번호} 입력
    - 2번 스크립트 클릭 후 `RUN` 클릭
6. 파이프라인 컴포넌트 빌드하기
    - 데이터셋 준비 컴포넌트: Fashion MNIST 데이터셋을 다운로드하는 함수 정의
        - **Note**: Fashion MNIST 데이터셋 다운로드 후 쿠버네티스 파이프라인에서 사용할 수 있도록 구성
      - 3-1번 스크립트 클릭 후 `RUN` 클릭
    - Fashion MNIST 모델 학습 및 서빙 구성
        - **Note**: Fashion MNIST 데이터셋 사용하여 CNN 모델 훈련
        - **Note**: 훈련된 모델을 TorchServe 통해 배포할 수 있도록 준비
      - 3-2번 스크립트 클릭 후 `RUN` 클릭 
    - 서빙을 위한 MAR 파일 생성 컴포넌트
        - **Note**: 훈련된 PyTorch 모델을 TorchServe에서 사용할 수 있는 MAR 파일로 패키징
      - 3-3번 스크립트 클릭 후 `RUN` 클릭 
    - KServe 컴포넌트 정의
        - **Note**: 모델 경로 기반 InferenceService 생성/업데이트, Ready 대기, 상태 조회 기능 정의
      - 3-4번 스크립트 클릭 후 `RUN` 클릭 
    - Foreground 실행용 ServingRuntime 생성
        - **Note**: 기본 PyTorch runtime 대신 `torchserve --start --foreground`로 동작하는 커스텀 ServingRuntime 생성
      - 3-5번 스크립트 클릭 후 `RUN` 클릭
    - KServe 인퍼런스 모델 생성 컴포넌트
        - **Note**: 위에서 만든 ServingRuntime을 사용해 실제 InferenceService를 생성하는 헬퍼 함수 정의
      - 3-6번 스크립트 클릭 후 `RUN` 클릭
7. 파이프라인 생성
      - 4번 스크립트 클릭 후 `RUN` 클릭
8. 파이프라인 실행
      - 5번 스크립트 클릭 후 `RUN` 클릭
      - `Run details.` 클릭
      - 모두 정상 실행됨을 확인
9. InferenceService Ready 대기
      - **Note**: 파이프라인이 끝까지 도는 데 시간이 걸리므로, 서빙 준비가 완료될 때까지 자동으로 기다려주는 셀입니다. 상태가 바뀔 때마다 로그가 찍히고, `Ready` 상태가 되면 자동으로 다음 단계로 넘어갈 수 있습니다.
      - 스크립트 클릭 후 `RUN` 클릭
      - `InferenceService Ready 상태 도달` 문구 확인

## 3. 모델 서빙 API 테스트
1. 모델 서빙 API 테스트
    - 모델 서빙 API 테스트 이미지 준비
      - 6-1번 스크립트 클릭 후 `RUN` 클릭
      - 6-1번 스크립트 결과 확인
    - 모델 서빙 API 테스트
      - 6-2번 스크립트 클릭 후 `RUN` 클릭
      - 6-2번 스크립트 결과 확인

## 4. K8s 측면 분석
   - **Note**: 명령어의 네임스페이스는 본인 것으로 바꿔서 사용하세요 (`kubectl config view --minify -o jsonpath='{..namespace}'`로 확인 가능). 예시로 쓰인 `kbm-u-kubeflow-tutorial`은 다른 계정 네임스페이스라 그대로 실행하면 권한 에러가 납니다.
1. 본인 네임스페이스 내의 모든 InferenceService 리소스를 YAML 형식으로 출력
    - 명령어 클릭 후 `Run` 클릭
    - 명령어 결과 확인
2. torchserve 파드들의 상태 확인
    - 명령어 클릭 후 `Run` 클릭
    - 명령어 결과 확인

## 5. 자원 정리
1. 노트북 하단 정리 스크립트 실행
    - **Note**: 실습에서 생성한 K8s 리소스(InferenceService, ServingRuntime 등)를 삭제하는 셀
    - 스크립트 클릭 후 `RUN` 클릭
    - 정리 완료 확인
