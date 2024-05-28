#!/bin/bash

echo "kakaocloud: 1. 환경 변수 설정 시작"
# 환경 변수 설정
command=$(cat <<EOF
export ACC_KEY='액세스 키 아이디 입력'
export SEC_KEY='보안 액세스 키 입력'
export EMAIL_ADDRESS='사용자 이메일 입력'
export CLUSTER_NAME='클러스터 이름 입력'
export API_SERVER='클러스터의 server 값 입력'
export AUTH_DATA='클러스터의 certificate-authority-data 값 입력'
export PROJECT_NAME='프로젝트 이름 입력'
EOF
)

# 환경 변수를 평가하고 .bashrc에 추가
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc
echo "kakaocloud: 환경 변수 설정 완료"

echo "kakaocloud: 2. 도커 설치 시작"
# 도커 설치
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 
sudo apt update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io 
sudo chmod 666 /var/run/docker.sock 
echo "kakaocloud: 도커 설치 완료"

echo "kakaocloud: 3. kubectl 설치 시작"
# kubectl 설치
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
echo "kakaocloud: kubectl 설치 완료"

echo "kakaocloud: 4. kic-iam-auth 설치 시작"
# kic-iam-auth 설치
sudo wget -O /usr/local/bin/kic-iam-auth https://objectstorage.kr-central-2.kakaoi.io/v1/fe631cd1b7a14c0ba2612d031a8a5619/public/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth
sudo chmod +x /usr/local/bin/kic-iam-auth
echo "kakaocloud: kic-iam-auth 설치 완료"

echo "kakaocloud: 5. kube config 설정 시작"
# kube config 설정
mkdir -p /home/ubuntu/.kube
wget -O /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/kube-config.yaml
envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config
chmod 600 /home/ubuntu/.kube/config
chown ubuntu:ubuntu /home/ubuntu/.kube/config
echo "kakaocloud: kube config 설정 완료"

echo "kakaocloud: 6. 하이퍼파라미터 파일 다운로드 시작"
# 하이퍼파라미터에 필요한 파일 다운로드
wget -O /home/ubuntu/Dockerfile https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Dockerfile 
wget -O /home/ubuntu/Experiment.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Experiment.yaml 
wget -O /home/ubuntu/mnist_train.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/mnist_train.py 
echo "kakaocloud: 하이퍼파라미터 파일 다운로드 완료"

echo "kakaocloud: 모든 설정이 완료되었습니다."
