# TensorFlow 이미지 사용
FROM tensorflow/tensorflow:latest

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 모든 파일을 작업 디렉토리로 복사
COPY . /app

# mnist_train.py 스크립트를 기본 실행 명령으로 설정
CMD ["python", "mnist_train.py"]
