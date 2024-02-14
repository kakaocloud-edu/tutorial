#!/bin/bash

echo "kakaocloud: Preparing directories and files"
sudo mkdir /home/ubuntu/yaml
sudo chmod 777 /home/ubuntu/yaml
echo "kakaocloud: Directories prepared"

echo "kakaocloud: Downloading YAML files"
sudo wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/lab6Yaml.tar -O /home/ubuntu/yaml/lab6Yaml.tar
sudo curl -o /home/ubuntu/yaml/lab6-Secret.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-Secret.yaml
sudo curl -o /home/ubuntu/yaml/lab6-Deployment.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-Deployment.yaml
sudo curl -o /home/ubuntu/yaml/lab6-ConfigMapDB.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-ConfigMapDB.yaml
echo "kakaocloud: YAML files downloaded"

echo "kakaocloud: Installing kubectl"
sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
echo "kakaocloud: kubectl installed"

echo "kakaocloud: Setting up .kube directory and configuration file"
sudo mkdir /home/ubuntu/.kube
sudo curl -o /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/kube-config.yaml
echo "kakaocloud: .kube setup completed"

echo "kakaocloud: Installing kic-iam-auth"
sudo wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O kic-iam-auth
sudo chmod +x kic-iam-auth
sudo mv kic-iam-auth /usr/local/bin/
echo "kakaocloud: kic-iam-auth installation completed"

echo "kakaocloud: Installing Docker and setting it up"
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
sudo echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo chmod 666 /var/run/docker.sock
echo "kakaocloud: Docker installation and setup completed"

echo "kakaocloud: Installing additional software"
sudo apt install unzip
sudo apt-get install -y openjdk-17-jdk maven
echo "kakaocloud: Additional software installation completed"

echo "kakaocloud: Setting permissions for .kube/config"
chmod 600 /home/ubuntu/.kube/config
chown ubuntu:ubuntu /home/ubuntu/.kube/config
echo "kakaocloud: Permissions set for .kube/config"

echo "kakaocloud: Downloading helm-values.yaml and applying environment substitutions"
sudo curl -o /home/ubuntu/values.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/helm-values.yaml
envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config
envsubst < /home/ubuntu/yaml/lab6-Deployment.yaml > /home/ubuntu/yaml/deploy.tmp && mv /home/ubuntu/yaml/deploy.tmp /home/ubuntu/yaml/lab6-Deployment.yaml
envsubst < /home/ubuntu/yaml/lab6-Secret.yaml > /home/ubuntu/yaml/secret.tmp && mv /home/ubuntu/yaml/secret.tmp /home/ubuntu/yaml/lab6-Secret.yaml
envsubst < /home/ubuntu/values.yaml > /home/ubuntu/values.tmp && mv /home/ubuntu/values.tmp /home/ubuntu/values.yaml
echo "kakaocloud: Environment substitutions applied and setup completed"
