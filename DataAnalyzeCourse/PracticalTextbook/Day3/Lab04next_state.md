# next_state 예측 모델 학습

실시간 정제된 데이터를 기반으로 하여 next state를 예측하는 모델 학습 과정입니다.

## 1. Notebook에서 next_state 예측 모델 학습 진행
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. next_state.ipynb 파일 다운로드

    #### **Lab4-0-3**
    ```bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/Lab04/next_state.ipynb
    ```

4. next_state.ipynb 파일 생성 확인 및 더블 클릭

    - next_state.ipynb 파일 좌측 상단에 있는 화살표를 눌러 셀 실행

5. 런타임 / 환경 구성

    - pip 명령어를 통해 `pyarrow`, `fasparquet`, `pandas`, `torch`, `optuna`, `scikit-learn` 설치
    - 설치 완료 후 뜨는 아래 사진과 같은 형식 확인

    <img width="1359" height="115" alt="0 설치" src="https://github.com/user-attachments/assets/c3c0e4b8-112c-4218-b089-5c8ae3bf9813" />

6. 경로 / 시드 / 하이퍼파라미터

    - 모델 학습에 필요한 경로 지정
    - 학습용 / 검증용 세션 분할을 위한 시드 지정
    - 하이퍼 파라미터 기본값 지정
    - 좌측 datasets 폴더 더블 클릭 후 next_state_pre 폴더 생성 확인

7. 데이터 로드 & 필수 컬럼 검증

    - data_check로 object storage에서 가져온 실시간 정제 데이터 로드

8. 세션 통계 & 짧은 세션 필터링

    - 세션 별 로그 길이의 분포를 파악
    - 학습에 도움이 되지 않는 짧은 로그의 세션 제거

9. 상태 인덱싱 (PAD/UNK 포함) & 저장

    - 상태를 인덱싱 하여 모델 학습에 유리하도록 수정
    - LSTM 모델에 필요한 PAD/UNK 포함 후 저장
    - 좌측 next_state_pre 폴더 더블 클릭 후 state_mapping.json 생성 확인
    - state_mapping.json 더블 클릭 후 내용 확인

10. 인덱싱 적용

    - current_state와 current_state_idx 출력 확인
    - next_state와 next_state_idx 출력 확인
    - state_mapping.json에 인덱싱 된 내용과 맞는지 비교

11. prev1/prev2 생성 & 관측 쌍 저장

    - 시퀀스 맥락을 반영하기 위한 prev1/prev2 생성
    - 분석 및 규칙 기반 마스킹에 활용하기 위한 관측 쌍을 저장
    - 좌측 next_state_pre 폴더에 observed_prev_pairs.npy 생성 확인

12. 세션 단위 Train / Val 분할

    - 세션 누수 방지를 위해 세션 단위로 분할
    - 좌측 next_state_pre 폴더에 train_val_sessions.json 생성 확인
    - train_val_sessions.json 더블 클릭 후 내용 확인

13. 탭형 피처 / 레이블 저장 (Parquet / CSV)

    - 모델 학습을 위한 파일 저장
    - 좌측 next_state_pre 폴더에 `X_train`, `X_val`, `y_train`, `y_val` 생성 확인
    - X_train.csv, y_train.csv 더블 클릭 후 내용 확인

14. 세션 시퀀스 구성

    - LSTM 모델이 학습 할 수 있는 시퀸스 데이터로 구성
    - 세션 단위로 시퀸스 데이터 생성

15. Dataset / DataLoader

    - 세션별 가변 길이 로그를 패딩된 배치 텐서로 변환
    - LSTM 모델이 처리할 수 있는 배치 형태로 수정하기 위한 작업

16. prev2/prev1 샘플 CSV 저장

    - 좌측 next_state_pre 폴더에 pre_pairs_sample.csv 생성 확인
    - pre_pairs_sample.csv 더블 클릭 후 내용 확인

17. 모델 정의 (LSTMClassifier)

    - next state 예측을 위한 LSTM 모델 정의

18. 클래스 불균형 가중치

    - 클래스 분균형 문제를 완화하기 위한 클래스별 가중치 계산

19. 모델 초기화 & 드라이런

    - 학습 전에 세팅 후 한 번 돌려보는 과정

20. 학습 / 평가 루틴

    - next_state 예측을 위한 훈련용 루프와 검증용 루프 정의

21. 기본 학습 루프 (조기 종료 / 체크포인트)

    - next_state 예측용 모델 학습 실행
    - Epoch가 돌아가면서 학습용 / 검증용 루프 동시 실행
    - top1의 정확도가 높은 모델이 best_model.pt에 저장
    - 좌측 next_state_pre 폴더에 best_model.pt 생성 확인

22. Optuna 하이퍼파라미터 탐색 (Top-1 최대화)

    - Optuna를 사용하여 정확도가 높게 나오는 하이퍼파라미터 탐색

23. 최종 재학습 (Optuna 베스트 적용)

    - 최적의 하이퍼파라미터를 적용하여 모델 학습 실행






