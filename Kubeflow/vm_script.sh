#!/bin/bash

# 환경 변수 설정
command=$(cat <<EOF
export ACC_KEY='사용자 액세스키 입력'
export SEC_KEY='사용자 시크릿키 입력'
export EMAIL_ADDRESS='사용자 이메일 입력'
export CLUSTER_NAME='k8s-cluster'
export API_SERVER='클러스터 api 엔드포인트 입력'
export AUTH_DATA='클러스터 auth-data 입력'
export PROJECT_NAME='프로젝트 이름 입력'
EOF
)

# 환경 변수를 평가하고 .bashrc에 추가
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc

# 도커 설치
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null 
sudo apt update
apt-get install -y docker-ce docker-ce-cli containerd.io 
chmod 666 /var/run/docker.sock 

# kubectl 설치
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# kic-iam-auth 설치
wget -O /usr/local/bin/kic-iam-auth https://objectstorage.kr-central-2.kakaoi.io/v1/fe631cd1b7a14c0ba2612d031a8a5619/public/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth
chmod +x /usr/local/bin/kic-iam-auth

# kube config 설정
mkdir -p /home/ubuntu/.kube
wget -O /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/kube-config.yaml
envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config
chmod 600 /home/ubuntu/.kube/config
chown ubuntu:ubuntu /home/ubuntu/.kube/config

# 하이퍼파라미터에 필요한 파일 설치
wget -O /home/ubuntu/Dockerfile https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Dockerfile 
wget -O /home/ubuntu/Experiment.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/Experiment.yaml 
wget -O /home/ubuntu/mnist_train.py https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Kubeflow/HyperParam/mnist_train.py 
