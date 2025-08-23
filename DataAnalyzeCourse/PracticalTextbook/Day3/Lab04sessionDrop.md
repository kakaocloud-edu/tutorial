# 세션 이탈 추론 모델 학습

실시간 정제된 데이터를 기반으로 하여 세션이 완료될지 중간에 이탈할지 추론하는 모델 학습 과정입니다.

## 1. Notebook에서 세션 이탈 추론 모델 학습 진행 (5분)

1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. sessionDrop.ipynb 파일 다운로드

### **Lab4-1-3**

```bash
wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab04/sessionDrop_predict.ipynb
```

- sessionDrop.ipynb 파일 생성 확인
1. sessionDrop.ipynb 파일 더블 클릭
    - sessionDrop.ipynb 파일 좌측 상단에 있는 실행 버튼(Shift + Enter)을 눌러 셀 실행
2. 환경 구성
    - 실습을 원활하게 진행하기 위해 라이브러리와 경로, 상수 값 등을 설정
3. 원본 데이터 로드
    - 원본 데이터를 로드하고 전체 세션의 개수를 집계
4. 간격/증분 계산
    - 세션 내 이벤트 간 시간차(`gap_sec`)와 누적 지표의 증가분(`delta_*`)을 만들어 정규화
5. Targit Label 생성 & 누수 세션 식별
    - 실제 결과인 Label 생성
    - 첫 활동부터 K 활동 내에 실제 결과 값이 포함된 누수 세션 식별
6. Feature Engineering
    - 모델 학습을 위해 데이터 전처리 작업 실행
7. 전처리 데이터 저장
    - 전처리한 데이터를 K 별로 저장
8. 학습용 / 검증용 데이터 셋 분할
    - 모델을 학습하기 위한 학습용 / 모델을 검증하기 위한 검증용 데이터 셋으로 분할
9. 모델 선택
    - 학습을 위한  모델을 선택
10. 모델 학습 & 평가
    - 선택한 모델로 학습을 진행
    - 평가 값에서 K 별 `Macro-F1`, `Accuracy` 값 확인
11. 모델 저장
    - K 별로 모델 저장
12. 세션 이탈 추론 결과 값 시각화
    - 검증 모델을 평가한 결과 값을 그래프로 시각화
    - 예측 성공 → 초록색 / 예측 실패 → 빨간색
