#!/bin/bash

echo "kakaocloud: test(1).variables validity test start"
required_variables=(
    ACC_KEY SEC_KEY EMAIL_ADDRESS CLUSTER_NAME API_SERVER AUTH_DATA PROJECT_NAME
    INPUT_DB_EP1 INPUT_DB_EP2 DOCKER_IMAGE_NAME DOCKER_JAVA_VERSION JAVA_VERSION
    SPRING_BOOT_VERSION,DB_EP1,DB_EP2
)


for variable in "${required_variables[@]}"; do
    : "${!variable:?"kakaocloud: 필수 환경변수 $variable 가 설정되지 않았습니다. 스크립트를 종료합니다."}"
done
echo "kakaocloud: test(1).variables is valid"



echo "kakaocloud: 3.github Connection test start"
curl --output /dev/null --silent --head --fail "https://github.com" || { echo "kakaocloud: github Connection failed"; exit 1; }
echo "kakaocloud: github Connection succeeded"


echo "kakaocloud: 4.Preparing directories and files"
sudo mkdir -p /home/ubuntu/yaml && sudo chmod 777 /home/ubuntu/yaml || { echo "kakaocloud: Failed to create directories."; exit 1; }
echo "kakaocloud: Directories prepared"



echo "kakaocloud: 5.Downloading YAML files"
sudo wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/lab6Yaml.tar -O /home/ubuntu/yaml/lab6Yaml.tar || { echo "kakaocloud: Failed to download lab6Yaml.tar"; exit 1; }
sudo curl -o /home/ubuntu/yaml/lab6-Secret.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-Secret.yaml || { echo "kakaocloud: Failed to download lab6-Secret.yaml"; exit 1; }
sudo curl -o /home/ubuntu/yaml/lab6-Deployment.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-Deployment.yaml || { echo "kakaocloud: Failed to download lab6-Deployment.yaml"; exit 1; }
sudo curl -o /home/ubuntu/yaml/lab6-ConfigMapDB.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-ConfigMapDB.yaml || { echo "kakaocloud: Failed to download lab6-ConfigMapDB.yaml"; exit 1; }
echo "kakaocloud: All YAML files downloaded"



echo "kakaocloud: 6.Installing kubectl"
sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" || { echo "kakaocloud: Failed to download kubectl binary"; exit 1; }
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl || { echo "kakaocloud: Failed to install kubectl binary"; exit 1; }
echo "kakaocloud: kubectl installed"


echo "kakaocloud: 7.Setting up .kube directory and configuration file"
sudo mkdir /home/ubuntu/.kube || { echo "Failed to create .kube directory"; exit 1; }
sudo curl -o /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/kube-config.yaml || { echo "Failed to download kube-config.yaml"; exit 1; }
echo "kakaocloud: .kube setup completed"



echo "kakaocloud: 8.Installing kic-iam-auth"
sudo wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O kic-iam-auth || { echo "Failed to download kic-iam-auth"; exit 1; }
sudo chmod +x kic-iam-auth || { echo "Failed to change permission of kic-iam-auth"; exit 1; }
sudo mv kic-iam-auth /usr/local/bin/ || { echo "Failed to move kic-iam-auth to /usr/local/bin/"; exit 1; }
echo "kakaocloud: kic-iam-auth installation completed"


echo "kakaocloud: 9.Installing Docker and setting it up"
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg || { echo "Failed to download Docker GPG key"; exit 1; }
sudo echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null || { echo "Failed to add Docker repository to sources.list"; exit 1; }
sudo apt-get update || { echo "Failed to update apt repository"; exit 1; }
sudo apt-get install -y docker-ce docker-ce-cli containerd.io || { echo "Failed to install Docker"; exit 1; }
sudo chmod 666 /var/run/docker.sock || { echo "Failed to change permission of docker.sock"; exit 1; }
echo "kakaocloud: Docker installation and setup completed"


echo "kakaocloud: 10.Installing additional software"
sudo apt install unzip || { echo "Failed to install unzip"; exit 1; }
sudo apt-get install -y openjdk-17-jdk maven || { echo "Failed to install openjdk-17-jdk and maven"; exit 1; }
echo "kakaocloud: Additional software installation completed"


echo "kakaocloud: 11.Setting permissions for .kube/config"
sudo chmod 600 /home/ubuntu/.kube/config || { echo "Failed to change permission of /home/ubuntu/.kube/config"; exit 1; }
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config || { echo "Failed to change ownership of /home/ubuntu/.kube/config"; exit 1; }
echo "kakaocloud: Permissions set for .kube/config"


echo "kakaocloud: 12.Downloading helm-values.yaml and applying environment substitutions"
sudo curl -o /home/ubuntu/values.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/helm-values.yaml || { echo "Failed to download helm-values.yaml"; exit 1; }
envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config || { echo "Failed to modify /home/ubuntu/.kube/config"; exit 1; }
envsubst < /home/ubuntu/yaml/lab6-Deployment.yaml > /home/ubuntu/yaml/deploy.tmp && mv /home/ubuntu/yaml/deploy.tmp /home/ubuntu/yaml/lab6-Deployment.yaml || { echo "Failed to modify /home/ubuntu/yaml/lab6-Deployment.yaml"; exit 1; }
envsubst < /home/ubuntu/yaml/lab6-Secret.yaml > /home/ubuntu/yaml/secret.tmp && mv /home/ubuntu/yaml/secret.tmp /home/ubuntu/yaml/lab6-Secret.yaml || { echo "Failed to modify /home/ubuntu/yaml/lab6-Secret.yaml"; exit 1; }
envsubst < /home/ubuntu/values.yaml > /home/ubuntu/values.tmp && mv /home/ubuntu/values.tmp /home/ubuntu/values.yaml || { echo "Failed to modify /home/ubuntu/values.yaml"; exit 1; }
echo "kakaocloud: Environment substitutions applied and setup completed"
