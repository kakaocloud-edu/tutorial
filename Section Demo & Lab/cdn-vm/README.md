# CDN Lab VM

Object Storage를 Origin으로 두고, VM의 Nginx를 Reverse Proxy Cache로 사용하는 CDN 실습용 패키지입니다.

학생은 VM 생성 시 사용자 스크립트에 `user-data.sh` 내용을 넣으면 됩니다. 설치가 끝나면 웹 콘솔에서 1단계부터 9단계까지 순서대로 실습을 진행할 수 있습니다. Origin URL, TTL, 캐시 크기를 입력하면 설정값이 내부 Nginx 설정으로 반영되고, 콘솔 버튼으로 MISS/HIT 확인, 응답 시간 비교, 캐시 Purge까지 수행할 수 있습니다.

## 튜토리얼

학생용 전체 실습 절차는 [TUTORIAL.md](./TUTORIAL.md)를 사용하세요.

이 문서는 Object Storage 파일 준비부터 VM 생성, CDN Lab Console 설정, MISS/HIT 확인, TTL 확인, Purge까지 순서대로 따라 할 수 있게 작성되어 있습니다.

## VM 보안 그룹

열어야 하는 포트:

- `80/tcp`: CDN 캐시 엔드포인트. 실습자 PC 공인 IP 또는 실습장 대역 허용
- `8080/tcp`: CDN Lab 웹 콘솔. 실습자 PC 공인 IP 또는 실습장 대역 허용
- `22/tcp`: SSH 접속이 필요한 경우. 관리자 또는 실습자 PC 공인 IP 허용

## 사용자 스크립트

실습 자료는 `kakaocloud-edu/tutorial` 저장소의 `Section Demo & Lab/cdn-vm` 경로에서 사용합니다. VM 사용자 스크립트에 아래 내용을 넣습니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

export CDN_LAB_REPO_ARCHIVE="https://github.com/kakaocloud-edu/tutorial/archive/refs/heads/main.tar.gz"
curl -fsSL "https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Section%20Demo%20%26%20Lab/cdn-vm/install.sh" | sudo -E bash
```

## 사용 흐름

1. Object Storage 버킷에 CSS와 JavaScript가 포함된 단일 `index.html` 파일을 올립니다.
2. `cdn-vm`, `Ubuntu 24.04`, `t1i.medium`, `30GB`, Public Subnet 스펙으로 VM을 생성하고 사용자 스크립트로 CDN Lab을 설치합니다.
3. 브라우저에서 `http://CDN_VM_PUBLIC_IP:8080`에 접속합니다.
4. 화면의 9단계 실습 목차를 따라 진행합니다.
5. Origin URL에 Object Storage URL을 입력합니다.
   예: `https://objectstorage.kr-central-2.kakaocloud.com/v1/533406004453430abd3d647bcf0b9bfc/bucket1`
6. TTL을 설정하고 `Origin/TTL 적용`을 누릅니다.
7. `첫 요청 실행`, `재요청 실행`, `2회 연속 측정`, `캐시 Purge` 버튼으로 CDN 동작을 확인합니다.

## 프론트 실습 목차

| 단계 | 내용 | 핵심 개념 |
| --- | --- | --- |
| 1 | CDN VM 생성 | Edge 서버 |
| 2 | Object Storage Origin URL과 TTL 설정 | Origin, TTL |
| 3 | Nginx Proxy 설정 | Reverse Proxy |
| 4 | 첫 요청 확인 | Cache MISS |
| 5 | 재요청 확인 | Cache HIT |
| 6 | 응답 시간 비교 | 캐시 성능 |
| 7 | 원본 수정 | 캐시 일관성 |
| 8 | TTL 확인 | 캐시 만료 |
| 9 | 캐시 삭제 | Invalidation/Purge |

## 실습 명령

```bash
curl -I http://CDN_VM_PUBLIC_IP/index.html
curl -I http://CDN_VM_PUBLIC_IP/index.html
curl -w "time_total: %{time_total}\n" -o /dev/null -s http://CDN_VM_PUBLIC_IP/index.html
```

처음 요청은 `X-Cache-Status: MISS`, 반복 요청은 `X-Cache-Status: HIT`가 나오는지 확인합니다.

## 서버 내부 파일

- `/opt/cdn-lab`: 관리자 웹 콘솔 코드
- `/etc/cdn-lab/config.json`: 웹 콘솔 설정값
- `/etc/nginx/conf.d/cdn-lab.conf`: 자동 생성되는 Nginx CDN 설정
- `/var/cache/nginx/cdn-lab`: Nginx 캐시 저장소

## 관리 명령

```bash
sudo systemctl status cdn-lab-admin
sudo systemctl restart cdn-lab-admin
sudo nginx -t
sudo systemctl reload nginx
sudo rm -rf /var/cache/nginx/cdn-lab/*
```

웹 콘솔의 `캐시 Purge` 버튼은 `/var/cache/nginx/cdn-lab` 내부 파일을 삭제하고 Nginx를 reload합니다.
