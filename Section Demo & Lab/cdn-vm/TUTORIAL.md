# CDN 실습 튜토리얼

이 문서는 Object Storage를 Origin으로 사용하고, VM의 Nginx Reverse Proxy Cache를 CDN Edge 서버처럼 구성하는 실습 절차입니다.

아래 순서대로 그대로 따라 하면 다음을 확인할 수 있습니다.

- Object Storage가 정적 파일 Origin 역할을 하는 구조
- VM이 CDN Edge 서버처럼 요청을 받아 Origin으로 프록시하는 구조
- 첫 요청의 `MISS`
- 반복 요청의 `HIT`
- TTL에 따른 캐시 만료
- Purge를 통한 캐시 삭제

## 0. 실습 구조

<img width="734" height="456" alt="image" src="https://github.com/user-attachments/assets/976b69bf-3f5a-4fb3-a921-99d9ff66aae9" />


## 1. 준비물

실습 전에 아래 항목을 준비합니다.

| 항목 | 설명 |
| --- | --- |
| Object Storage Bucket | 정적 파일을 저장할 Origin |
| CDN VM | `cdn-vm` 이름으로 생성 |
| 보안 그룹 | `80/tcp`, `8080/tcp`, 필요 시 `22/tcp`를 접속할 IP와 함께 허용 |
| 웹 브라우저 | CDN Lab Console 접속용 |
| 터미널 | `curl` 명령 확인용 |

## 2. Object Storage에 실습 파일 올리기

Object Storage Bucket에는 `index.html` 파일 하나만 업로드합니다. 업로드한 파일은 인증 없이 브라우저에서 열 수 있도록 공개 접근이 가능해야 합니다.

```text
index.html
```

### 2-1. index.html 만들기

아래 내용을 복사해서 `index.html` 파일로 저장한 뒤 Object Storage에 업로드합니다. CSS와 JavaScript가 모두 포함된 단일 파일이므로 별도의 `style.css`, `app.js`, `image.png` 파일은 필요하지 않습니다.

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CDN Cache 실습</title>
  <style>
body {
  margin: 0;
  background: #f2f2f2;
  color: #111;
  font-family: Arial, "Noto Sans KR", sans-serif;
}

main {
  max-width: 760px;
  margin: 60px auto;
  padding: 40px;
  background: #fff;
  border: 1px solid #ddd;
}

.label {
  display: inline-block;
  margin: 0 0 16px;
  padding: 8px 18px;
  border-radius: 999px;
  background: #ffe100;
  font-weight: 700;
}

h1 {
  margin: 0 0 16px;
  font-size: 48px;
}

button {
  padding: 12px 18px;
  border: 0;
  background: #111;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}

pre {
  margin-top: 16px;
  padding: 16px;
  background: #f7f7f7;
  border: 1px solid #ddd;
}
  </style>
</head>
<body>
  <main>
    <p class="label">Origin: Object Storage</p>
    <h1>CDN Cache 실습</h1>
    <p>이 파일은 Object Storage에 저장된 원본 콘텐츠입니다.</p>
    <button id="timeButton">현재 시간 표시</button>
    <pre id="result">버튼을 눌러보세요.</pre>
  </main>
  <script>
const button = document.querySelector("#timeButton");
const result = document.querySelector("#result");

button.addEventListener("click", () => {
  result.textContent = `Browser time: ${new Date().toLocaleString()}`;
});
  </script>
</body>
</html>
```

## 3. Object Storage Origin URL 확인

Object Storage에 올린 `index.html`이 HTTP 또는 HTTPS로 접근되는지 확인합니다.

브라우저 주소창에 아래 형식의 링크를 입력해서 페이지가 열리는지 확인합니다.

```text
OBJECT_STORAGE_ORIGIN_URL/index.html
```

링크 예시:

```text
https://objectstorage.kr-central-2.kakaocloud.com/v1/533406004453430abd3d647bcf0b9bfc/bucket1/index.html
```

터미널에서는 기존처럼 `curl -I`로 확인할 수 있습니다. 아래 명령에서 `OBJECT_STORAGE_ORIGIN_URL`을 본인의 Object Storage URL로 바꿉니다.

```bash
curl -I OBJECT_STORAGE_ORIGIN_URL/index.html
```

예시:

```bash
curl -I https://objectstorage.kr-central-2.kakaocloud.com/v1/533406004453430abd3d647bcf0b9bfc/bucket1/index.html
```

정상이라면 `200 OK` 또는 이에 준하는 성공 응답이 나와야 합니다.

```text
HTTP/1.1 200 OK
Content-Type: text/html
```

`401 Unauthorized` 또는 `403 Forbidden`이 나오면 Object Storage 버킷이나 `index.html` 오브젝트가 공개 접근 가능하도록 설정되어 있는지 확인합니다.

뒤에서 CDN Lab Console에 입력할 `Object Storage Origin URL`은 파일명을 제외한 버킷 URL입니다. 예를 들어 위 링크가 정상이라면 콘솔에는 아래처럼 입력합니다.

```text
https://objectstorage.kr-central-2.kakaocloud.com/v1/533406004453430abd3d647bcf0b9bfc/bucket1
```

## 4. CDN VM 생성

아래 스펙으로 CDN VM을 생성합니다.

| 항목 | 값 |
| --- | --- |
| 이름 | `cdn-vm` |
| 이미지 | `Ubuntu 24.04` |
| 인스턴스 유형 | `t1i.medium` |
| 볼륨 | `30GB` |
| 키페어 | 기존 키페어가 있으면 사용 |
| 네트워크 | Public Subnet 선택 |

보안 그룹 또는 방화벽에서 아래 포트와 접속 IP를 함께 허용합니다.

| 포트 | 허용 IP | 용도 |
| --- | --- | --- |
| `80/tcp` | 실습자 PC 공인 IP 또는 실습장 대역 | CDN 캐시 엔드포인트 |
| `8080/tcp` | 실습자 PC 공인 IP 또는 실습장 대역 | CDN Lab Console |
| `22/tcp` | 관리자 또는 실습자 PC 공인 IP | SSH 접속이 필요한 경우 |

실습 환경에서 접속 IP 제한이 어렵다면 교육장 네트워크 대역으로 제한합니다. 모든 IP(`0.0.0.0/0`) 허용은 실습 편의상 가능하지만, 공개 인터넷에 노출되므로 실습 후 보안 그룹을 정리합니다.

고급설정 -> 사용자 스크립트에서 VM 생성 화면의 사용자 스크립트 또는 cloud-init 입력란에 아래 내용을 그대로 붙여넣습니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

export CDN_LAB_REPO_ARCHIVE="https://github.com/kakaocloud-edu/tutorial/archive/refs/heads/main.tar.gz"
curl -fsSL "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Section%20Demo%20%26%20Lab/cdn-vm/install.sh" | sudo -E bash
```

설치에는 보통 2분에서 5분 정도 걸립니다.

## 5. CDN Lab Console 접속

VM 생성이 끝나면 브라우저에서 아래 주소로 접속합니다.

```text
http://CDN_VM_PUBLIC_IP:8080
```

예시:

```text
http://203.0.113.10:8080
```

화면 상단에 `CDN 실습 콘솔`이 보이면 설치가 완료된 상태입니다.

## 6. Origin URL과 TTL 설정

CDN Lab Console의 2단계 영역에서 아래 값을 입력합니다.

| 입력 항목 | 예시 값 |
| --- | --- |
| Object Storage Origin URL | `https://objectstorage.kr-central-2.kakaocloud.com/v1/533406004453430abd3d647bcf0b9bfc/bucket1` |
| TTL seconds | `60` |
| Cache size | `100m` |
| Inactive | `60m` |

입력 후 `Origin/TTL 적용` 버튼을 누릅니다.

버튼을 누르면 서버 내부에서 아래 작업이 자동으로 수행됩니다.

```text
1. /etc/cdn-lab/config.json 저장
2. /etc/nginx/conf.d/cdn-lab.conf 생성 또는 갱신
3. nginx -t 실행
4. systemctl reload nginx 실행
```

## 7. 첫 요청 확인: Cache MISS

CDN Lab Console의 4단계에서 경로를 확인합니다.

기본값:

```text
/index.html
```

`첫 요청 실행` 버튼을 누릅니다.

예상 결과:

```text
X-Cache-Status: MISS
X-CDN-Server: VM-CDN-Lab
```

터미널에서 직접 확인하려면 아래 명령을 사용합니다.

```bash
curl -I http://CDN_VM_PUBLIC_IP/index.html
```

처음 요청이 `MISS`인 이유는 CDN VM에 아직 해당 파일 캐시가 없기 때문입니다. 이때 CDN VM은 Object Storage Origin으로 요청을 보내 원본 파일을 가져오고, 응답을 캐시에 저장합니다.

이미 같은 경로를 브라우저나 `curl`로 요청했거나 이전 실습 캐시가 남아 있다면 첫 요청에서도 `HIT`가 나올 수 있습니다. 이 경우 9단계의 `캐시 Purge`를 실행한 뒤 다시 확인합니다.

## 8. 재요청 확인: Cache HIT

CDN Lab Console의 5단계에서 `재요청 실행` 버튼을 누릅니다.

예상 결과:

```text
X-Cache-Status: HIT
X-CDN-Server: VM-CDN-Lab
```

터미널에서 직접 확인하려면 같은 명령을 다시 실행합니다.

```bash
curl -I http://CDN_VM_PUBLIC_IP/index.html
```

두 번째 요청이 `HIT`인 이유는 CDN VM이 이미 `/index.html`을 캐시에 저장했기 때문입니다. 이 경우 Object Storage까지 가지 않고 CDN VM이 바로 응답합니다.

## 9. 응답 시간 비교

CDN Lab Console의 6단계에서 `2회 연속 측정` 버튼을 누릅니다.

이 버튼은 교육 목적상 먼저 캐시를 비운 뒤 같은 파일을 두 번 요청합니다.

예상 흐름:

```text
측정 전 캐시를 Purge했습니다.
1회차: MISS / 느림
2회차: HIT / 빠름
```

터미널에서 직접 비교하려면 아래 명령을 두 번 실행합니다.

```bash
curl -w "time_total: %{time_total}\n" -o /dev/null -s http://CDN_VM_PUBLIC_IP/index.html
```

반복 요청에서 시간이 줄어드는지 비교합니다.

## 10. 원본 수정과 캐시 일관성 확인

Object Storage의 `index.html` 내용을 아래처럼 수정해서 다시 업로드합니다.

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>CDN Origin Updated</title>
</head>
<body>
  <h1>Origin Updated</h1>
  <p>Object Storage의 원본 파일을 수정했습니다.</p>
</body>
</html>
```

그 다음 CDN URL로 다시 접속합니다.

```text
http://CDN_VM_PUBLIC_IP/index.html
```

TTL이 아직 지나지 않았다면 이전 내용이 보일 수 있습니다.

이 현상은 CDN 캐시가 빠른 응답을 위해 원본 콘텐츠를 일정 시간 보관하기 때문에 발생합니다.

## 11. TTL 확인

CDN Lab Console의 8단계에서 `현재 TTL 확인` 버튼을 누릅니다. 이 버튼은 현재 설정된 TTL 값을 보여주는 기능이며, 실제 만료 여부를 자동으로 검증하지는 않습니다.

예상 결과:

```text
현재 TTL: 60초
Nginx 설정: proxy_cache_valid 200 206 60s;
```

TTL이 60초라면, 캐시된 `200` 또는 `206` 응답은 60초 동안 유효합니다.

실제 만료 동작은 TTL 시간이 지난 뒤 같은 경로를 다시 요청해서 응답 내용이나 `X-Cache-Status` 변화를 비교합니다. TTL이 지난 뒤 다시 요청하면 Nginx는 Origin에 다시 요청하거나 재검증을 수행합니다.

## 12. 캐시 삭제: Invalidation/Purge

CDN Lab Console의 9단계에서 `캐시 Purge` 버튼을 누릅니다.

예상 결과:

```text
캐시가 삭제되었습니다. 다음 요청은 다시 MISS로 시작합니다.
```

이후 `Purge 후 요청 확인` 버튼을 누르면 다음과 같은 결과가 나와야 합니다.

```text
X-Cache-Status: MISS
```

터미널에서 직접 캐시를 삭제하려면 CDN VM에 SSH 접속 후 아래 명령을 실행합니다.

```bash
sudo rm -rf /var/cache/nginx/cdn-lab/*
sudo systemctl reload nginx
```

## 13. 설치 상태 확인 명령

CDN VM에 SSH로 접속한 뒤 아래 명령을 사용할 수 있습니다.

```bash
sudo systemctl status cdn-lab-admin
```

CDN Lab Console 관리자 서비스가 실행 중인지 확인합니다.

```bash
sudo systemctl status nginx
```

CDN 캐시 엔드포인트 역할을 하는 Nginx 서비스가 실행 중인지 확인합니다.

```bash
sudo nginx -t
```

Nginx 설정 파일에 문법 오류가 없는지 검사합니다.

```bash
sudo cat /etc/cdn-lab/config.json
```

CDN Lab Console에 저장된 Origin URL, TTL, 캐시 크기 설정값을 확인합니다.

```bash
sudo cat /etc/nginx/conf.d/cdn-lab.conf
```

CDN Lab Console이 생성한 실제 Nginx Reverse Proxy Cache 설정을 확인합니다.

```bash
sudo ls -al /var/cache/nginx/cdn-lab
```

Nginx가 저장한 캐시 파일이 있는지 확인합니다.

## 14. 문제 해결

### Console에 접속되지 않는 경우

확인할 항목:

- VM이 완전히 부팅되었는지 확인
- 보안 그룹에서 `8080/tcp`가 실습자 PC 공인 IP 또는 실습장 대역에 열려 있는지 확인
- CDN VM 내부에서 관리자 서비스 상태 확인

```bash
sudo systemctl status cdn-lab-admin
```

서비스를 재시작합니다.

```bash
sudo systemctl restart cdn-lab-admin
```

### CDN URL에 접속되지 않는 경우

확인할 항목:

- 보안 그룹에서 `80/tcp`가 실습자 PC 공인 IP 또는 실습장 대역에 열려 있는지 확인
- Nginx가 실행 중인지 확인

```bash
sudo systemctl status nginx
```

Nginx 설정 문법을 확인합니다.

```bash
sudo nginx -t
```

### Origin URL 적용이 실패하는 경우

Object Storage URL이 브라우저 또는 `curl`에서 직접 열리는지 먼저 확인합니다.

```bash
curl -I OBJECT_STORAGE_ORIGIN_URL/index.html
```

Origin URL 입력 시 마지막에 파일명을 넣지 않습니다.

올바른 예:

```text
https://objectstorage.kr-central-2.kakaocloud.com/v1/533406004453430abd3d647bcf0b9bfc/bucket1
```

잘못된 예:

```text
https://objectstorage.kr-central-2.kakaocloud.com/v1/533406004453430abd3d647bcf0b9bfc/bucket1/index.html
```

### 계속 MISS만 나오는 경우

확인할 항목:

- 요청 경로가 매번 같은지 확인
- `Cache-Control: no-store` 같은 헤더가 Origin에서 내려오지 않는지 확인
- Nginx 설정이 정상 적용되었는지 확인

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 15. 실습 정리

이번 실습에서 확인한 핵심 개념은 다음과 같습니다.

| 개념 | 의미 |
| --- | --- |
| Origin | 원본 콘텐츠가 저장된 위치 |
| Edge Server | 사용자 요청을 먼저 받는 CDN 서버 |
| Reverse Proxy | 사용자 요청을 대신 Origin으로 전달하는 구조 |
| Cache MISS | CDN 캐시에 파일이 없어 Origin에서 가져오는 상태 |
| Cache HIT | CDN 캐시에 파일이 있어 바로 응답하는 상태 |
| TTL | 캐시가 유효한 시간 |
| Purge | 캐시를 강제로 삭제하는 작업 |

실제 CDN 서비스는 전 세계 여러 Edge 서버, 자동 Purge API, 보안 정책, HTTPS 인증서, 도메인 연결 기능을 추가로 제공합니다. 이 실습은 그중 가장 핵심인 `Origin -> Edge Cache -> Browser` 흐름을 VM 한 대에서 축소해 확인하는 구조입니다.
