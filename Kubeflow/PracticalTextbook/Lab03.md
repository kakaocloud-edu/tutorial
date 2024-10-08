# Kubeflow 사용자/그룹 추가
Kakocloud 콘솔을 이용한 Kubeflow의 사용자와 그룹을 추가하는 실습입니다.

### 1. kakaocloud 콘솔에서 사용자 추가 (약 1분 소요)
   - **Note** : 관리자/맴버 권한이 없는 유저를 추가하는 경우 생성 불가
1. 카카오 클라우드 콘솔 AI Service > Kubeflow > Kubeflow
2. Kubeflow 탭 > 생성한 kubeflow (kc-handson) > `+ 사용자 추가` 클릭
3. Kubeflow 소유자 타입으로 생성 (도메인에 IAM 유저 중에 `관리자/맴버 권한이 있는 유저` 이메일 추가)
   - 사용자 타입 : `Kubeflow 소유자`
   - 사용자 이메일 : `사용자 이메일 입력`
   - 네임스페이스 생성(선택) : `test`
   - 네임스페이스 파일 스토리지 : `handson`
   - `확인` 클릭
4. 사용자 추가상태 (`Active`) 확인
5. 카카오 클라우드 콘솔 > AI Service > Kubeflow > Kubeflow
6. Kubeflow 탭 > 생성해둔 `Kubeflow(kc-handson)` 클릭
7. `대시보드 보기` 클릭 후 `Public Dashboard` 둘 중 하나 클릭
8. 사용자 추가 단계에서 입력한 사용자 이메일 계정과 해당 이메일로 전송된 임시 비밀번호로 로그인 후 접속 확인
   - Email Address : `소유자 이메일 계정`
   - Password : `소유자 이메일로 전송된 초기 패스워드`
   - `Login` 클릭
   - 로그인 확인

### 2. kakaocloud 콘솔에서 그룹 추가 (약 1분 소요)
1. 카카오 클라우드 콘솔 > AI Service > Kubeflow > Kubeflow
2. Kubeflow 탭 > 생성해둔 `Kubeflow(kc-handson)` 클릭
3. 그룹 탭 > `그룹 추가` 버튼 클릭
4. 그룹 설정 정보 작성
      - 네임스페이스 이름 : `kc-handson-grp`
      - 네임스페이스 파일 스토리지 : `kc-handson-fs 관련 링크 선택`
      - 그룹 쿼터 할당 : `쿼터 할당 미사용`
      - `확인` 클릭
5. Kubeflow 생성 시 추가한 Kubeflow 소유자를 그룹에 추가
      - 그룹 우측 더보기 버튼 클릭
      - `그룹 사용자 추가` 버튼 클릭
      - 그룹 사용자 설정 정보
         - 사용자 타입: `기존 등록된 사용자`
         - 사용자 이메일: `Kubeflow 생성 시 입력한 사용자 이메일`
         - 그룹 사용자 권한: `Admin`
      - `확인` 클릭
7. 그룹 사용자 추가 확인
   - 우측 더보기 버튼 클릭
   - `그룹 사용자 설정` 클릭
   - 상태 값 `Active` 확인

### 3. Kubeflow 콘솔에서 세부 내용 확인
1. 추가된 사용자로 로그인된 Kubeflow 콘솔에서 로그아웃
2. 그룹에 추가된 Kubeflow 소유자 이메일 계정과 복사해둔 임시 비밀번호로 로그인
3. Kubeflow 대시보드 최상단 네임스페이스에 생성된 접근 가능한 네임스페이스 목록 2개 확인
   - Kubeflow 대시보드 최상단 네임스페이스 클릭
   -  **Note** : `kbm-g-kc-handson-grp`, `kbm-u-kubeflow-tutorial` 확인

4. Manage Account 탭에서 추가된 접근 가능한 네임스페이스 목록 확인

5. Manage Group Users 탭에서 추가된 그룹 네임스페이스 사용자 확인
