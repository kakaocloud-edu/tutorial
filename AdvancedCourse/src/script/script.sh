#!/bin/bash

sudo mkdir /home/ubuntu/yaml
sudo chmod 777 /home/ubuntu/yaml
sudo wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/lab6Yaml.tar -O /home/ubuntu/yaml/lab6Yaml.tar

sudo curl -o /home/ubuntu/yaml/lab6-Secret.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/lab6-Secret.yaml

sudo curl -o /home/ubuntu/yaml/lab6-Deployment.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/lab6-Deployment.yaml

sudo curl -o /home/ubuntu/yaml/lab6-ConfigMapDB.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/lab6-ConfigMapDB.yaml

sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

sudo mkdir /home/ubuntu/.kube

sudo curl -o /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/config.yaml

sudo wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O kic-iam-auth
sudo chmod +x kic-iam-auth
sudo mv kic-iam-auth /usr/local/bin/

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
sudo echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo chmod 666 /var/run/docker.sock

sudo apt install unzip
sudo apt-get install -y openjdk-17-jdk maven

sudo chmod 600 /home/ubuntu/.kube/config
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config

sudo curl -o /home/ubuntu/yaml/values.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/values.yaml

sudo sed -i "s|\${AUTH_DATA}|$AUTH_DATA|g" /home/ubuntu/.kube/config
sudo sed -i "s|\${API_SERVER}|$API_SERVER|g" /home/ubuntu/.kube/config
sudo sed -i "s|\${ACC_KEY}|$ACC_KEY|g" /home/ubuntu/.kube/config
sudo sed -i "s|\${SEC_KEY}|$SEC_KEY|g" /home/ubuntu/.kube/config
sudo sed -i "s|\${PROJECT_NAME}|$PROJECT_NAME|g" /home/ubuntu/yaml/lab6-Deployment.yaml
sudo sed -i "s|\${DB_EP1}|$DB_EP1|g" /home/ubuntu/yaml/lab6-Secret.yaml
sudo sed -i "s|\${DB_EP2}|$DB_EP2|g" /home/ubuntu/yaml/lab6-Secret.yaml
sudo sed -i "s|\${PROJECT_NAME}|$PROJECT_NAME|g" /home/ubuntu/yaml/values.yaml
sudo sed -i "s|\${INPUT_DB_EP1}|$INPUT_DB_EP1|g" /home/ubuntu/yaml/values.yaml
sudo sed -i "s|\${INPUT_DB_EP2}|$INPUT_DB_EP2|g" /home/ubuntu/yaml/values.yaml


