# Monitoring Flow

Monitoring Flow를 이용하여 로드밸런서, API 서버, Hadoop 클러스터 등을 모니터링하는 실습입니다.

---

## LAB 1. 퍼블릭 가용성 모니터링 (without Flow Connection)

**목표**: Load Balancer 퍼블릭 엔드포인트의 **API 응답 상태**를 모니터링한다.  

### 구성
1. 시나리오 생성  
   - *VPC 활용* 체크 해제 (Flow Connection 없이)  
   - 스케줄: 1분마다
2. Default Variable
   ```yaml
   LB_IP = {Load Balancer의 Public IP}
   ```
3. 스텝
   - API: `LB_CHECK`
     - Method: `GET`
     - URL: `http://${LB_IP}`
     - Expected Code: `200`
     - Timeout: `3000`
4. 테스트 실행 → 실행 결과 이벤트 확인

**성공 기준**  
- 응답 코드 `200` → `Succeeded`

---

## LAB 2. 내부 자원 헬스체크 (Flow Connection 사용)

**목표**: VPC 내부 API 서버 및 Hadoop 클러스터 헬스체크.

### 구성
1. Flow Connection 생성
2. 시나리오 생성 (Flow Connection 연결)
   - 스케줄: 1분마다
3. Default Variable
   ```yaml
   API_IP   = {api-server-1의 private IP}
   HADOOP_ID = {Hadoop 클러스터 ID}
   ```
4. 스텝
   - **API_CHECK**
     - URL: `http://${API_IP}`
     - Expected Code: `200`
   - **Sleep**
     - 0분 10초
   - **HADOOP_CHECK**
     - URL: `https://hadoop-eco.kr-central-2.kakaocloud.com/v2/hadoop-eco/clusters/${HADOOP_ID}/vms`
     - Headers:  
       - `content-type: application/json`  
       - `credential-id: {IAM Access Key ID}`  
       - `credential-secret: {IAM Secret Key}`

**성공 기준**
- Flow Connection **Active**  
- 모든 스텝 `Succeeded`  
- 서브넷/보안 미설정 시 `Failed` 재현 확인

---

## LAB 3. 쇼핑몰 API 서버 다수 Endpoint 시나리오 체크

**목표**: 카테고리 조회 → 상품 조회 → 로그인 → 회원가입 등 **사용자 여정 기반 API 시퀀스** 모니터링.

### Default Variable
```yaml
LB_IP        = 61.109.239.101
CATEGORY_NAME = Electronics
USER_ID       = u1
```

### 스텝
1. **카테고리 목록 조회**
   - GET `http://${LB_IP}/categories`
2. **상품 조회 (특정 카테고리)**
   - GET `http://${LB_IP}/category?name=${CATEGORY_NAME}`
3. **로그인**
   - POST `http://${LB_IP}/login`
   - Body: `user_id=${USER_ID}`
4. **회원가입 (인증 오류 검증용)**
   ```yaml
   USER_NAME = u1
   EMAIL     = u1@kakao.com
   GENDER    = M
   AGE       = 25
   ```
   - POST `http://${LB_IP}/add_user`
   - Body: `user_id=${USER_ID}&name=${USER_NAME}&email=${EMAIL}&gender=${GENDER}&age=${AGE}`

**성공 기준**
- 모든 단계 `Succeeded`  
- 세션/쿠키 누락 → `Failed` 재현  

---

## LAB 4. 멀티 타깃 모니터링 (For + JSON List)

**목표**: 여러 API 서버를 하나의 시나리오에서 반복 점검.

### Default Variable
```yaml
END_POINTS = ["{api-server-1의 private IP}", "{api-server-2의 private IP}"]   # JSON List
TARGET_IP  = ""   # String
```

### 스텝
1. **FOR Loop**
   - foreach: `END_POINTS`
   - marker → `TARGET_IP`
2. **하위 API 호출**
   - GET `http://${TARGET_IP}` (Expected Code: 200)

**성공 기준**
- 모든 엔드포인트 정상 응답 시 `Succeeded`
