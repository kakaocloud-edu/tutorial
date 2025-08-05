#!/bin/bash

echo "kakaocloud: 1. 환경 변수 설정 시작"
# 환경 변수 설정
command=$(cat <<EOF
export ACC_KEY='액세스 키 아이디 입력'
export SEC_KEY='보안 액세스 키 입력'
export EMAIL_ADDRESS='사용자 이메일 입력'
export AUTH_DATA='클러스터의 certificate-authority-data 값 입력'
export API_SERVER='클러스터의 server 값 입력'
export CLUSTER_NAME='클러스터 이름 입력'
export PROJECT_NAME='프로젝트 이름 입력'



export S3_BUCKET='data-catalog-bucket'
export S3_KEY='preprocessed/processed_user_behavior.parquet'
export REGION='kr-central-2'
export S3_ENDPOINT_URL='https://objectstorage.kr-central-2.kakaocloud.com'
export IMAGE_NAME="\${PROJECT_NAME}.kr-central-2.kcr.dev/kakao-registry/next-state:1.0"
EOF
)

# 환경 변수를 평가하고 .bashrc에 추가
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc
source /home/ubuntu/.bashrc
echo "kakaocloud: 환경 변수 설정 완료"

echo "kakaocloud: 2. 도커 설치 시작"
# 도커 설치
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 
sudo apt update
apt-get install -y docker-ce docker-ce-cli containerd.io 
chmod 666 /var/run/docker.sock 
echo "kakaocloud: 도커 설치 완료"

echo "kakaocloud: 3. kubectl 설치 시작"
# kubectl 설치
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
echo "kakaocloud: kubectl 설치 완료"

echo "kakaocloud: 4. kic-iam-auth 설치 시작"
# kic-iam-auth 설치
wget -O /usr/local/bin/kic-iam-auth https://objectstorage.kr-central-2.kakaocloud.com/v1/c11fcba415bd4314b595db954e4d4422/public/docs/binaries-kic-iam-auth/Linux%20x86_64%2064Bit/kic-iam-auth
chmod +x /usr/local/bin/kic-iam-auth
echo "kakaocloud: kic-iam-auth 설치 완료"

echo "kakaocloud: 5. kube config 설정 시작"
# kube config 설정
mkdir -p /home/ubuntu/.kube
if [ -f /home/ubuntu/.kube/config ]; then
    rm /home/ubuntu/.kube/config
fi
wget -O /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/kube-config.yaml
envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config
chmod 600 /home/ubuntu/.kube/config
chown ubuntu:ubuntu /home/ubuntu/.kube/config
echo "kakaocloud: kube config 설정 완료"

echo "kakaocloud: 6. 하이퍼파라미터 파일 다운로드 시작"
# 기존 파일 삭제
if [ -f /home/ubuntu/Dockerfile ]; then
    rm /home/ubuntu/Dockerfile
fi
if [ -f /home/ubuntu/Experiment.yaml ]; then
    rm /home/ubuntu/Experiment.yaml
fi
if [ -f /home/ubuntu/mnist_train.py ]; then
    rm /home/ubuntu/mnist_train.py
fi

# 하이퍼파라미터에 필요한 파일 다운로드
# HyperParam 관련 파일 다운로드
wget -O /home/ubuntu/Dockerfile \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/HyperParam/Dockerfile

wget -O /home/ubuntu/requirements.txt \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/HyperParam/requirements.txt

wget -O /home/ubuntu/next_state_train.py \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/HyperParam/next_state_train.py

wget -O /home/ubuntu/Experiment.template.yaml \
     https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/DataAnalyzeCourse/HyperParam/Experiment.template.yaml


# Experiment.yaml 파일 생성
envsubst < /home/ubuntu/Experiment.template.yaml > /home/ubuntu/Experiment.yaml
rm /home/ubuntu/Experiment.template.yaml
echo "kakaocloud: 하이퍼파라미터 파일 다운로드 완료"

echo "kakaocloud: 모든 설정이 완료되었습니다."
