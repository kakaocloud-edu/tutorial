# next_state 예측 모델 학습

실시간 정제된 데이터를 기반으로 하여 next state를 예측하는 모델 학습 과정입니다.

## 1. Notebook에서 next_state 예측 모델 학습 진행
1. Notebooks 탭 > `cpu-notebook`의 `CONNECT` 클릭
2. Other 중 `Terminal` 클릭
3. next_state.ipynb 파일 다운로드

    #### **Lab4-0-3**
    ```bash
    wget https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/src/day3/ipynb/next_state.ipynb
    ```

4. next_state.ipynb 파일 생성 확인 및 더블 클릭
5. 런타임 / 환경 구성

    - pip 명령어를 통해 `pyarrow`, `fasparquet`, `pandas`, `torch`, `optuna`, `scikit-learn` 설치
    - 설치 완료 후 뜨는 `Successfully installed Mako-1.3.10 alembic-1.16.4 colorlog-6.9.0 cramjam-2.11.0 fastparquet-2024.11.0 fsspec-2025.7.0 greenlet-3.2.4 mpmath-1.3.0 nvidia-cublas-cu12-12.8.4.1 nvidia-cuda-cupti-cu12-12.8.90 nvidia-cuda-nvrtc-cu12-12.8.93 nvidia-cuda-runtime-cu12-12.8.90 nvidia-cudnn-cu12-9.10.2.21 nvidia-cufft-cu12-11.3.3.83 nvidia-cufile-cu12-1.13.1.3 nvidia-curand-cu12-10.3.9.90 nvidia-cusolver-cu12-11.7.3.90 nvidia-cusparse-cu12-12.5.8.93 nvidia-cusparselt-cu12-0.7.1 nvidia-nccl-cu12-2.27.3 nvidia-nvjitlink-cu12-12.8.93 nvidia-nvtx-cu12-12.8.90 optuna-4.5.0 pandas-2.3.2 pyarrow-15.0.2 scikit-learn-1.7.1 sqlalchemy-2.0.43 sympy-1.14.0 torch-2.8.0 triton-3.4.0`을 통해 설치 완료 확인
    
6. 경로 / 시드 / 하이퍼파라미터

    - 모델 학습에 필요한 경로 지정
    - 학습용 / 검증용 세션 분할을 위한 시드 지정
    - 하이퍼 파라미터 기본값 지정

7. 데이터 로드 & 필수 컬럼 검증

    - data_check로 object storage에서 가져온 실시간 정제 데이터 로드

8. 세션 통계 & 짧은 세션 필터링

    - 세션 별 로그 길이의 분포를 파악
    - 학습에 도움이 되지 않는 짧은 로그의 세션 제거

9. 상태 인덱싱 (PAD/UNK 포함) & 저장

    - 상태를 인덱싱 하여 모델 학습에 유리하도록 수정
    - LSTM 모델에 필요한 PAD/UNK 포함 후 저장
