#!/bin/bash

# 환경 변수 설정
command=$(cat <<EOF
export ACC_KEY='사용자 액세스 키 ID 입력'
export SEC_KEY='사용자 액세스 보안 키 입력'
export EMAIL_ADDRESS='사용자 이메일 입력(직접 입력)'
export CLUSTER_NAME='클러스터 이름 입력'
export API_SERVER='클러스터의 API 엔드포인트 입력'
export AUTH_DATA='클러스터의 certificate-authority-data 입력'
export PROJECT_NAME='프로젝트 이름 입력'
EOF
)

# 환경 변수를 평가하고 .bashrc에 추가
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc

# kubectl 설치
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# kic-iam-auth 설치
wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O kic-iam-auth
chmod +x kic-iam-auth
mv kic-iam-auth /usr/local/bin/

# kube config 설정
mkdir -p /home/ubuntu/.kube
wget -O /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/kube-config.yaml
envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config
chmod 600 /home/ubuntu/.kube/config
chown ubuntu:ubuntu /home/ubuntu/.kube/config
