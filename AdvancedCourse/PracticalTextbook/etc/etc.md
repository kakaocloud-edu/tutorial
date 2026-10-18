
# ☸️ 쿠버네티스 실습: Pod → ReplicaSet → Deployment

이 실습은 `busybox:1.35` 이미지를 사용해 쿠버네티스의 핵심 리소스(`Pod`, `ReplicaSet`, `Deployment`)를 체험하는 과정입니다.  
각 리소스의 역할과 차이점을 실습을 통해 익혀봅시다.

<img width="590" height="308" alt="image" src="https://github.com/user-attachments/assets/ab9bf16b-f847-4088-b744-10ce8cdad818" />
<img width="842" height="234" alt="image" src="https://github.com/user-attachments/assets/851838ec-e931-49c6-9156-730bd8a2bb69" />


## 1. Pod 생성

단일 Pod를 생성하고 기본 명령어를 통해 상태를 확인합니다.

### `pod.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: busybox-pod
  labels:
    app: busybox
spec:
  containers:
  - name: busybox
    image: busybox:1.35
    command: ["sh", "-c", "while true; do echo Hello from BusyBox at $(date); sleep 5; done"]
```

#### 적용
```bash
kubectl apply -f pod.yaml
```

#### 🧪 실습 명령어
```bash
kubectl get pods
kubectl describe pod busybox-pod
kubectl logs busybox-pod
kubectl exec -it busybox-pod -- sh
kubectl delete pod busybox-pod
```

---

## 2. ReplicaSet 생성

ReplicaSet으로 여러 Pod를 관리하고 자동 복구 기능을 체험합니다.

### `replicaset.yaml`

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: busybox-rs
spec:
  replicas: 2
  selector:
    matchLabels:
      app: busybox
  template:
    metadata:
      labels:
        app: busybox
    spec:
      containers:
      - name: busybox
        image: busybox:1.35
        command: ["sleep", "3600"]
```

#### 적용
```bash
kubectl apply -f replicaset.yaml
```

#### 실습 명령어
```bash
kubectl get rs
kubectl get pods
kubectl scale rs busybox-rs --replicas=3
kubectl delete pod <pod-name>  # 삭제된 Pod는 자동 복구됨
kubectl edit rs busybox-rs    # 이미지 수정 후 기존 Pod는 유지됨
```

> **✏️ 참고**: `kubectl edit rs`로 이미지를 `busybox:1.36`으로 변경해도 기존 Pod는 업데이트되지 않습니다. ReplicaSet은 Pod 복제를 유지하는 데 강력하지만, 버전 업데이트에는 적합하지 않습니다.

---

## 3. Deployment 생성

Deployment로 선언적 배포와 롤링 업데이트, 롤백 기능을 체험합니다.

### `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: busybox-deploy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: busybox
  template:
    metadata:
      labels:
        app: busybox
    spec:
      containers:
      - name: busybox
        image: busybox:1.35
        command: ["sleep", "3600"]
```

#### 적용
```bash
kubectl apply -f deployment.yaml
```

#### 실습 명령어
```bash
kubectl get deployments
kubectl get rs
kubectl get pods
kubectl rollout status deployment busybox-deploy
kubectl set image deployment/busybox-deploy busybox=busybox:1.36
kubectl rollout history deployment busybox-deploy
kubectl rollout undo deployment busybox-deploy
```

> **참고**: Deployment는 이미지 변경 시 Rolling Update로 Pod를 교체하며, 버전 이력을 관리하고 쉽게 롤백할 수 있습니다.

---

## 리소스 정리 요약

| 리소스       | 기능                       | 실습 포인트                           |
|--------------|----------------------------|---------------------------------------|
| **Pod**      | 가장 기본적인 실행 단위     | `logs`, `exec`, `describe`로 관찰     |
| **ReplicaSet** | 지정된 Pod 수 유지         | 수동 수정 어려움, 자동 복구 체험      |
| **Deployment** | 선언적 배포 관리           | 롤링 업데이트, 롤백, 버전 이력 확인   |

---

## 리소스 삭제

실습 후 생성된 리소스를 정리합니다.

```bash
kubectl delete pod busybox-pod
kubectl delete rs busybox-rs
kubectl delete deployment busybox-deploy
```
