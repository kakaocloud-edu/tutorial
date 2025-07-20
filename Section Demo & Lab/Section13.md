# Object Storage & CDN으로 정적 웹사이트 호스팅

카카오클라우드 Object Storage와 CDN을 이용하여 정적 웹 사이트를 호스팅하는 방법을 다룹니다.


## 기본 정보
- **예상 소요 시간**: 약 30분


## 시나리오 소개

이 튜토리얼은 HTML과 이미지로 구성된 예제 웹사이트를 Object Storage에 업로드하고 퍼블릭 액세스를 설정한 후, CDN 서비스를 연동하여 외부에서 빠르게 접근할 수 있도록 구성하는 실습입니다.

### 주요 단계

1. Object Storage 버킷 생성 및 접근 설정  
2. HTML 및 이미지 파일 업로드  
3. CDN 서비스 생성 및 버킷 오리진 연동  
4. CDN 도메인을 통한 정적 웹사이트 배포 및 확인


## Step 1. Object Storage 버킷 생성

1. 카카오클라우드 콘솔 접속 후 **Object Storage** 메뉴 선택  
2. "일반 버킷"에서 **[버킷 생성]** 클릭  
3. 다음 정보 입력 후 **[생성]** 클릭:

| 항목   | 값              |
|--------|-----------------|
| 유형   | Hot             |
| 이름   | `object-test`  |
| 암호화 | 미사용          |

Object Storage 서비스에서 버킷을 만드는 자세한 방법은 [Object Storage > 버킷 생성](https://docs.kakaocloud.com/service/bss/object-storage/how-to-guides/object-storage-manage-bucket#create-bucket) 참고.

---

## Step 2. 버킷 접근 설정 (퍼블릭 액세스 허용)

1. 콘솔 > Object Storage > **버킷 목록**에서 해당 버킷 클릭  
2. **권한 탭 > 접근(Access-Control)** > [접근 설정] 클릭  
3. **퍼블릭 액세스 허용 (Read only)** 선택 후 [저장]  
4. 팝업창에서 [확인] 클릭

> ⚠️ 주의: 모든 IP 허용 시 보안 이슈가 발생할 수 있으므로 특정 IP 허용 설정을 권장합니다.

---

## Step 3. 예제 정적 웹 사이트 다운로드 및 구성

이번 단계에서는 웹 브라우저를 사용하여 예제 웹사이트를 직접 다운로드하고, 로컬에 필요한 폴더 구조를 만드는 방법을 안내합니다. 별도의 명령어 입력 없이 웹 기반으로 진행할 수 있습니다.

---

#### 1. 로컬 폴더 만들기

- 먼저, **내 컴퓨터의 적절한 위치** (예: 바탕화면 또는 `다운로드` 폴더)에
  `object-cdn`이라는 이름의 새 폴더를 생성합니다.

---

#### 2. 예제 HTML 파일 다운로드

1. 아래 링크를 클릭합니다:  
   - [index.html 열기](https://github.com/kakaocloud-edu/tutorial/blob/main/Section%20Demo%20%26%20Lab/object-cdn/index.html)

2. 페이지가 열리면, 오른쪽 상단의 **Raw** 버튼 클릭
3. 브라우저에 HTML 코드만 표시되면,  
   `Ctrl+S` (Windows) 또는 `Cmd+S` (Mac) 를 눌러 저장합니다.

4. 파일 이름을 `index.html`로 하고, 아까 만든 `object-cdn` 폴더에 저장합니다.

---

#### 3. 이미지 폴더 만들기

- `object-cdn` 폴더 안에 `images`라는 **새 폴더**를 생성합니다.

---

#### 4. 예제 이미지 다운로드

1. 아래 링크를 클릭합니다:  
   - [main.png 열기](https://github.com/kakaocloud-edu/tutorial/blob/main/Section%20Demo%20%26%20Lab/object-cdn/images/main.png)

2. 이미지가 열리면,  
   마우스 오른쪽 클릭 → **이미지 저장** 또는 **다른 이름으로 저장** 선택

3. `main.png`라는 이름으로 저장하고, `object-cdn/images` 폴더 안에 넣으세요.

---

#### 5. 최종 폴더 구조 확인
```
object-cdn/
├── index.html
└── images/
    └── main.png
```


## Step 4. 예제 사이트 업로드

1. 콘솔 > **Beyond Storage Service > Object Storage**로 이동  
2. 버킷 목록에서 `object-test` 버킷 클릭  
3. **객체 탭 > [파일 업로드]** 클릭  
4. **[폴더 추가]** 선택 → `~/Downloads/object-cdn` 폴더 업로드  
5. **[업로드]** 클릭

---

#### 4. 접속 확인

1. 버킷 > 객체 탭에서 `object-cdn/index.html` 위치 확인  
2. `index.html` → [더 보기] > 객체 URL 복사  
3. 복사한 URL을 브라우저에 붙여넣어 접속 확인

---

## Step 5. CDN 설정

#### 1. CDN 서비스 생성

1. 콘솔 > **CDN 메뉴** 선택  
2. **[서비스 생성]** 클릭  
3. 1단계 설정:

| 항목                 | 값                  |
|----------------------|---------------------|
| 서비스 이름          | object-cdn        |
| 호스트 서버          | 카카오클라우드 CDN              |
| 오리진 서버          | 카카오클라우드 Object Storage   |
| 버킷               | `object-test` 선택 |
| 오리진 서버 프로토콜 | HTTPS               |
| 오리진 서버 포트     | 443                 |
| 오리진 경로(선택)    | `/object-cdn`       |
| Gzip 압축            | 사용                |

4. 2단계(캐시)와 3단계(Access Control)는 기본값 유지 후 [다음]  
5. 4단계: 정보 검토 후 [생성]

서비스 목록에서 생성된 CDN의 **[더 보기] > 시작 또는 재시작** 선택  
[시작] 버튼 클릭 → "서비스를 성공적으로 만들었습니다." 메시지 확인

---

#### 2. 서비스 도메인 접속 확인

- CDN > 서비스 목록에서 **서비스 도메인 주소 복사**
- 브라우저에서 접속:

```
http://{CDN 서비스 도메인}/index.html
```

정적 웹사이트가 정상적으로 표시되는지 확인합니다.

<img width="1910" height="1519" alt="image" src="https://github.com/user-attachments/assets/3fe876bd-79d1-4128-bafb-da8eab375000" />
