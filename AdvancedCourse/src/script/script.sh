#!/bin/bash

echo "kakaocloud: 3.Variables validity test start"
required_variables=(
    ACC_KEY SEC_KEY CLUSTER_NAME API_SERVER AUTH_DATA PROJECT_NAME
    INPUT_DB_EP1 INPUT_DB_EP2 DOCKER_IMAGE_NAME DOCKER_JAVA_VERSION JAVA_VERSION
    SPRING_BOOT_VERSION DB_EP1 DB_EP2
)

for var in "${required_variables[@]}"; do
    [[ -z "${!var}" ]] && { echo "kakaocloud: 필수 환경변수 $var 가 설정되지 않았습니다. 스크립트를 종료합니다."; exit 1; }
done
echo "kakaocloud: Variables are valid"


echo "kakaocloud: 4.Github Connection test start"
curl --output /dev/null --silent --head --fail "https://github.com" || { echo "kakaocloud: Github Connection failed"; exit 1; }
echo "kakaocloud: Github Connection succeeded"


echo "kakaocloud: 5.Preparing directories and files"
sudo mkdir -p /home/ubuntu/yaml && sudo chmod 777 /home/ubuntu/yaml || { echo "kakaocloud: Failed to create directories."; exit 1; }
echo "kakaocloud: Directories prepared"


echo "kakaocloud: 6.Downloading YAML files"
if [ ! -d "/home/ubuntu/tutorial" ]; then
    sudo git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || { echo "kakaocloud: Failed to git clone"; exit 1; }
else
    echo "kakaocloud: /home/ubuntu/tutorial already exists, skipping git clone"
fi

if [ ! -d "/home/ubuntu/tutorial/AdvancedCourse/src/manifests" ]; then
    echo "kakaocloud: Cloning again as the previous clone seems to have failed"
    sudo rm -rf /home/ubuntu/tutorial
    sudo git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || { echo "kakaocloud: Failed to git clone"; exit 1; }
fi

sudo cp /home/ubuntu/tutorial/AdvancedCourse/src/manifests/lab6-* /home/ubuntu/yaml || { echo "kakaocloud: Failed to set yaml"; exit 1; }
echo "kakaocloud: All YAML files downloaded"


echo "kakaocloud: 7.Preparing Spring directories and files"
sudo cp -r /home/ubuntu/tutorial/AdvancedCourse/src/spring /home/ubuntu/ || { echo "kakaocloud: Failed to create Spring directories."; exit 1; }
sudo chmod +x /home/ubuntu/spring/mvnw || { echo "kakaocloud: Failed to change permission of mvnw"; exit 1; }
echo "kakaocloud: Spring Directories and files prepared"

echo "kakaocloud: 8.Installing kubectl"
sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" || { echo "kakaocloud: Failed to download kubectl binary"; exit 1; }
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl || { echo "kakaocloud: Failed to install kubectl binary"; exit 1; }
echo "kakaocloud: Kubectl installed"


echo "kakaocloud: 9.Installing kic-iam-auth"
sudo wget -O /usr/local/bin/kic-iam-auth https://objectstorage.kr-central-2.kakaocloud.com/v1/c11fcba415bd4314b595db954e4d4422/public/docs/binaries-kic-iam-auth/Linux%20x86_64%2064Bit/kic-iam-auth || { echo "kakaocloud: Failed to download kic-iam-auth"; exit 1; }
sudo chmod +x /usr/local/bin/kic-iam-auth || { echo "kakaocloud: Failed to change permission of kic-iam-auth"; exit 1; }
echo "kakaocloud: kic-iam-auth installation completed"


echo "kakaocloud: 10.Installing Docker and setting it up"
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg || { echo "kakaocloud: Failed to download Docker GPG key"; exit 1; }
sudo echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null || { echo "kakaocloud: Failed to add Docker repository to sources.list"; exit 1; }
sudo apt-get update || { echo "kakaocloud: Failed to update apt repository"; exit 1; }
sudo apt-get install -y docker-ce docker-ce-cli containerd.io || { echo "kakaocloud: Failed to install Docker"; exit 1; }
sudo chmod 666 /var/run/docker.sock || { echo "kakaocloud: Failed to change permission of docker.sock"; exit 1; }
echo "kakaocloud: Docker installation and setup completed"


echo "kakaocloud: 11.Installing additional software"
sudo apt install unzip || { echo "kakaocloud: Failed to install unzip"; exit 1; }
sudo apt install jq -y || { echo "kakaocloud: Failed to install jq"; exit 1; }
sudo apt-get install -y openjdk-17-jdk maven || { echo "kakaocloud: Failed to install openjdk-17-jdk and maven"; exit 1; }
sudo apt install tree || { echo "kakaocloud: Failed to install tree"; exit 1; }
echo "kakaocloud: Additional software installation completed"


echo "kakaocloud: 12.Setting .kube/config"
sudo mkdir -p /home/ubuntu/.kube || { echo "kakaocloud: Failed to create .kube directory"; exit 1; }
sudo cp /home/ubuntu/tutorial/AdvancedCourse/src/manifests/kube-config.yaml /home/ubuntu/.kube/config || { echo "kakaocloud: Failed to set kube-config.yaml"; exit 1; }
envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv -f /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config || { echo "kakaocloud: Failed to modify /home/ubuntu/.kube/config"; exit 1; }
sudo chmod 600 /home/ubuntu/.kube/config || { echo "kakaocloud: Failed to change permission of /home/ubuntu/.kube/config"; exit 1; }
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config || { echo "kakaocloud: Failed to change ownership of /home/ubuntu/.kube/config"; exit 1; }
echo "kakaocloud: Setting .kube/config completed"


echo "kakaocloud: 13.Downloading helm-values.yaml and applying environment substitutions"
sudo cp /home/ubuntu/tutorial/AdvancedCourse/src/manifests/helm-values.yaml /home/ubuntu/values.yaml || { echo "kakaocloud: Failed to download helm-values.yaml"; exit 1; }
envsubst < /home/ubuntu/yaml/lab6-manifests.yaml > /home/ubuntu/yaml/manifests.tmp && mv -f /home/ubuntu/yaml/manifests.tmp /home/ubuntu/yaml/lab6-manifests.yaml || { echo "kakaocloud: Failed to modify /home/ubuntu/yaml/lab6-manifests.yaml"; exit 1; }
envsubst < /home/ubuntu/values.yaml > /home/ubuntu/values.tmp && mv -f /home/ubuntu/values.tmp /home/ubuntu/values.yaml || { echo "kakaocloud: Failed to modify /home/ubuntu/values.yaml"; exit 1; }
echo "kakaocloud: Environment substitutions applied and setup completed"

echo "kakaocloud: 14.Checking Kubernetes cluster nodes status"
kubeconfig="/home/ubuntu/.kube/config"
KUBECONFIG=$kubeconfig kubectl get nodes || { echo "kakaocloud: Failed to communicate with Kubernetes cluster"; exit 1; }
echo "kakaocloud: Successfully communicated with Kubernetes cluster"

echo "kakaocloud: 15.Deploying ingress-nginx controller"
KUBECONFIG=$kubeconfig kubectl apply -f \
  https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/ingress-nginx-controller.yaml \
  || { echo "kakaocloud: Failed to deploy ingress-nginx controller"; exit 1; }
echo "kakaocloud: ingress-nginx controller deployed"
