# 머신 러닝 모델 학습

실시간 정제된 데이터를 기반으로 하여 세션 이탈 추론 모델, 다음 상태 예측 모델 학습 과정입니다.

## 1. 세션 이탈 추론 모델 학습 진행 (15분)

1. sessionDrop.ipynb 파일 더블 클릭 후 실행
    - 실행 버튼(Shift + Enter)을 눌러 셀 실행
2. 패키지 설치
    - 실습에 필요한 패키지 설치
3. 환경 구성
    - 실습을 원활하게 진행하기 위해 라이브러리와 경로, 상수 값 등을 설정
    - models 폴더 생성 확인
4. 원본 데이터 로드
    - 원본 데이터를 로드하고 전체 세션의 개수를 집계
5. 간격/증분 계산
    - 세션 내 이벤트 간 시간차(`gap_sec`)와 누적 지표의 증가분(`delta_*`)을 만들어 정규화
6. Targit Label 생성 & 누수 세션 식별
    - 실제 결과인 Label 생성
    - 첫 활동부터 K 활동 내에 실제 결과 값이 포함된 누수 세션 식별
7. Feature Engineering
    - 모델 학습을 위해 데이터 전처리 작업 실행
8. 전처리 데이터 저장
    - 전처리한 데이터를 K 별로 저장
    - datasets/sessionDrop 경로에 전처리 데이터 저장된 것을 확인
9. 학습용 / 검증용 데이터 셋 분할
    - 모델을 학습하기 위한 학습용 / 모델을 검증하기 위한 검증용 데이터 셋으로 분할
10. 모델 선택 & 학습
    - 모델 선택 후 학습용 데이터 셋으로 학습
11. 모델 검증 & 평가
    - 학습을 마친 모델을 검증용 데이터 셋으로 검증
    - 평가 값에서 K 별 `Macro-F1`, `Accuracy` 값 확인
12. 모델 저장
    - K 별로 모델 저장
    - models/sessionDrop 경로에 K 별 모델이 저장된 것을 확인
13. 세션 이탈 추론 결과 값 시각화
    - 검증 모델을 평가한 결과 값을 그래프로 시각화
    - Total 평가 값과 K별 평가 값을 확인
14. 추론 테스트
    - 모델에 샘플 데이터를 입력하여 추론 테스트 진행


## 2. next_state 예측 모델 학습 진행 (20분)

1. next_state.ipynb 파일 더블 클릭 후 실행

    - next_state.ipynb 파일 좌측 상단에 있는 실행 버튼(Shift + Enter)을 눌러 셀 실행

2. 런타임 / 환경 구성

    - pip 명령어를 통해 `pyarrow`, `fasparquet`, `pandas`, `torch`, `optuna`, `scikit-learn` 설치
    - 설치 완료 후 뜨는 아래 사진과 같은 형식 확인

    <img width="1359" height="115" alt="0 설치" src="https://github.com/user-attachments/assets/c3c0e4b8-112c-4218-b089-5c8ae3bf9813" />

3. 경로 / 시드 / 하이퍼파라미터

    - 모델 학습에 필요한 경로 지정
    - 학습용 / 검증용 세션 분할을 위한 시드 지정
    - 하이퍼 파라미터 기본값 지정
    - 좌측 datasets 폴더 더블 클릭 후 next_state_pre 폴더 생성 확인

4. 데이터 로드 & 필수 컬럼 검증

    - data_check로 object storage에서 가져온 실시간 정제 데이터 로드

5. 세션 통계 & 짧은 세션 필터링

    - 세션 별 로그 길이의 분포를 파악
    - 학습에 도움이 되지 않는 짧은 로그의 세션 제거

6. 상태 인덱싱 (PAD/UNK 포함) & 저장

    - 상태를 인덱싱 하여 모델 학습에 유리하도록 수정
    - LSTM 모델에 필요한 PAD/UNK 포함 후 저장
    - 좌측 next_state_pre 폴더 더블 클릭 후 state_mapping.json 생성 확인
    - state_mapping.json 더블 클릭 후 내용 확인

7. 인덱싱 적용

    - current_state와 current_state_idx 출력 확인
    - next_state와 next_state_idx 출력 확인
    - state_mapping.json에 인덱싱 된 내용과 맞는지 비교

8. prev1/prev2 생성 & 관측 쌍 저장

    - 시퀀스 맥락을 반영하기 위한 prev1/prev2 생성
    - 분석 및 규칙 기반 마스킹에 활용하기 위한 관측 쌍을 저장
    - 좌측 next_state_pre 폴더에 observed_prev_pairs.npy 생성 확인

9. 세션 단위 Train / Val 분할

    - 세션 누수 방지를 위해 세션 단위로 분할
    - 좌측 next_state_pre 폴더에 train_val_sessions.json 생성 확인
    - train_val_sessions.json 더블 클릭 후 내용 확인

10. 탭형 피처 / 레이블 저장 (Parquet / CSV)

    - 모델 학습을 위한 파일 저장
    - 좌측 next_state_pre 폴더에 `X_train`, `X_val`, `y_train`, `y_val` 생성 확인
    - X_train.csv, y_train.csv 더블 클릭 후 내용 확인

11. 세션 시퀀스 구성

    - LSTM 모델이 학습 할 수 있는 시퀸스 데이터로 구성
    - 세션 단위로 시퀸스 데이터 생성

12. Dataset / DataLoader

    - 세션별 가변 길이 로그를 패딩된 배치 텐서로 변환
    - LSTM 모델이 처리할 수 있는 배치 형태로 수정하기 위한 작업

13. prev2/prev1 샘플 CSV 저장

    - 좌측 next_state_pre 폴더에 pre_pairs_sample.csv 생성 확인
    - pre_pairs_sample.csv 더블 클릭 후 내용 확인

14. 모델 정의 (LSTMClassifier)

    - next state 예측을 위한 LSTM 모델 정의

15. 클래스 불균형 가중치

    - 클래스 분균형 문제를 완화하기 위한 클래스별 가중치 계산

16. 모델 초기화 & 드라이런

    - 학습 전에 세팅 후 한 번 돌려보는 과정

17. 학습 / 평가 루틴

    - next_state 예측을 위한 훈련용 루프와 검증용 루프 정의

18. 기본 학습 루프 (조기 종료 / 체크포인트)

    - next_state 예측용 모델 학습 실행
    - Epoch가 돌아가면서 학습용 / 검증용 루프 동시 실행
    - top1의 정확도가 높은 모델이 best_model.pt에 저장
    - 좌측 next_state_pre 폴더에 best_model.pt 생성 확인

19. Optuna 하이퍼파라미터 탐색 (Top-1 최대화)

    - Optuna를 사용하여 정확도가 높게 나오는 하이퍼파라미터 탐색

20. 최종 재학습 (Optuna 베스트 적용)

    - 최적의 하이퍼파라미터를 적용하여 모델 학습 실행

