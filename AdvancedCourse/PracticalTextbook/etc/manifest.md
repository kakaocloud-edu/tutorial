# Kubernetes Manifest 이해 가이드

## 목표
이 문서를 통해 학생은 다음을 이해한다:

- Kubernetes Manifest가 무엇인지
- 기본 구조 (apiVersion, kind, metadata, spec)
- 각 필드의 의미
- Pod, Deployment, Service 구조
- label과 selector의 관계

---

# 1. Kubernetes Manifest란 무엇인가?

👉 Manifest = Kubernetes에게 원하는 상태를 설명하는 파일

👉 쉽게 말하면:
**“이렇게 만들어 주세요”라고 요청하는 설계도**

---

## 왜 Manifest를 사용하는가?

- 자동으로 상태 유지
- 사람이 읽기 쉬움
- 인프라를 코드로 관리 가능

---

## 한 줄 정리

👉 **Manifest = Kubernetes에 원하는 상태를 선언하는 YAML 파일**

---

# 2. Kubernetes의 핵심 동작 방식

Kubernetes는 선언형 시스템이다.

❌ “Pod 하나 실행해”  
✅ “Pod 2개 유지해”

---

👉 Kubernetes는 계속 확인한다:

현재 상태 ≠ 원하는 상태  
→ 자동으로 맞춘다

---

# 3. 기본 구조 (🔥 매우 중요)

모든 Kubernetes YAML은 아래 구조를 가진다:

```yaml
apiVersion: ...
kind: ...
metadata:
  name: ...
spec:
  ...
```
👉 구조 이해

Manifest
├── apiVersion
├── kind
├── metadata
└── spec

# 4. apiVersion
apiVersion: apps/v1

👉 의미:
어떤 API 규칙으로 리소스를 만들 것인지 정의

👉 예

v1 → Pod, Service

apps/v1 → Deployment

👉 한 줄 정리

apiVersion = 리소스를 만드는 규칙

# 5. kind
kind: Deployment

👉 의미:
무엇을 만들 것인지 정의

👉 예

Pod → 컨테이너 실행
Deployment → Pod 관리
Service → 네트워크 연결

👉 한 줄 정리

kind = 만들 리소스 종류

# 6. metadata
```yaml
metadata:
  name: my-app
  labels:
    app: web
```
👉 의미:
리소스를 식별하는 정보

👉 중요: labels

labels:
  app: web

👉 다른 리소스가 이 리소스를 찾을 때 사용

👉 한 줄 정리

metadata = 이름 + 식별 정보

# 7. spec (🔥 가장 중요)
```yaml
spec:
  replicas: 2
  containers:
    - name: nginx
      image: nginx
```
👉 의미:
“어떻게 동작해야 하는지” 정의

👉 한 줄 정리

spec = 원하는 상태

# 8. Pod 이해
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: nginx
      image: nginx
```
👉 설명

Pod = 컨테이너 실행 단위
containers = 실제 실행 내용

👉 한 줄 정리

Pod = 컨테이너 실행 단위

# 9. Deployment 이해
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deploy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: nginx
          image: nginx
```
👉 핵심 구조

Deployment
├── replicas (개수 유지)
├── selector (대상 선택)
└── template (Pod 설계도)

👉 중요 포인트

template = Pod 정의

selector = 관리 대상

👉 한 줄 정리

Deployment = Pod을 자동으로 관리하는 관리자

# 10. Service 이해
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: web
  ports:
    - port: 80        # 사용자가 접근하는 포트
      targetPort: 80  # 실제 Pod 컨테이너 포트
```
👉 설명

port → 외부에서 접근하는 포트

targetPort → 실제 Pod 내부 포트

👉 핵심

selector:
  app: web

👉 label 기반 연결

👉 한 줄 정리

Service = Pod으로 트래픽을 전달하는 역할

# 11. label과 selector
```yaml
Pod:
labels:
  app: web
```
```yaml
Service:
selector:
  app: web
```
👉 의미

label이 같으면 연결된다

👉 한 줄 정리

Kubernetes는 label로 연결된다

# 12. 전체 흐름

사용자 요청
↓
Service
↓
Pod

# 13. Manifest 적용
kubectl apply -f file.yaml

👉 의미:
YAML을 Kubernetes에 적용

14. 상태 확인
kubectl get pods
kubectl describe pod
# 15. 핵심 정리

👉 반드시 기억해야 할 4가지

apiVersion → 규칙

kind → 종류

metadata → 이름/식별

spec → 원하는 상태

# 16. 실수 TOP 5

❌ apiVersion 틀림
❌ kind 오타
❌ labels 불일치
❌ selector mismatch
❌ 들여쓰기 오류

# 17. 실습 예제

👉 다음 Manifest를 해석해보세요
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
  labels:
    app: demo
spec:
  containers:
    - name: nginx
      image: nginx
```
✔️ 해석

test-pod라는 Pod 생성
nginx 컨테이너 실행
app=demo 라벨 부여
