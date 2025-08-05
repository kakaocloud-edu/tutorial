# 베이스 이미지: 가벼운 파이썬 환경
FROM python:3.8-slim

WORKDIR /app

# 필요한 라이브러리
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 학습 스크립트 복사
COPY . /app

# 컨테이너 실행 시 호출될 엔트리포인트
CMD ["python", "next_state_train.py"]
