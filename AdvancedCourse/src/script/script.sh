#!/bin/bash

export PROJECT_NAME="kakaocloud-online"
export ACC_KEY="97dc46cc56bd4a01b1fbd959eb7e546f"
export SEC_KEY="uRlGhHKMVsSmOo55S_6vx1IdqxwcJNlcuDRwWWhQ_v9bj6d-2KmjXINrg8MD_BMwKN4VWAA4rgobZM7saMDZGA"
export API_SERVER="https://569dc30c-60a2-4576-890b-081906720742-public.ke.kr-central-2.kakaocloud.com:443"
export AUTH_DATA="LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM2akNDQWRLZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJME1ESXdNakU0TURreU1Wb1hEVE0wTURFek1ERTRNVFF5TVZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTm81CjJVVVNQSGRUbHduMnRER1k1eHZSNXd0VEFoTFNjWUJyTHl0ZmtGYVhoNkp3V1pIcnJDRXNNUHMwTUhDUFJZaUMKV2RUazBBb0ZOejVTaGVKV0VPZzFONFVRZFRHbUVibklZZ2lWMmtWS0tybmJQbmxjTExmQkZQbHRXQ3k5QTJXbgpKbUQwYloxaE0rODF2UmJiczUrU3kvYzJ6SUdXUmVTdkhYd2p2MkxtV09ZcTdUZVh5V0g5YUNLWFJNdFl4T01iCnh1V29mUkl3MnUyazlrcGhmVGI4SFZGWEQybWM0TG96ZVRLMWJEVzFaOFdlNEJMdFJXZ3hTSUlZVzM5dEp0K3gKVWJmVCtYVWR1REVxQUNkQlVYWXRwWlBEbGkxSFhCVnpJZ1hwY0xzeGFiSHFoL0YyaUZwNjFObDhtWk5uekhkYwpGMGNseGxwdzlRbGNSZDRrWXFjQ0F3RUFBYU5GTUVNd0RnWURWUjBQQVFIL0JBUURBZ0trTUJJR0ExVWRFd0VCCi93UUlNQVlCQWY4Q0FRQXdIUVlEVlIwT0JCWUVGRHY5MDZKOWF1M0ZGTmZGUkVPRzh4QzdTaWFOTUEwR0NTcUcKU0liM0RRRUJDd1VBQTRJQkFRREJFOUlmYmxLVXVVT1BCa2NPNkJWbFhQdHBVR2ZZVk1VUzZSUGtTbVpQay9rdApEdjUzUlkzaXl2TkNGUUdNbmNueTlNcmlDSnlMNWJaUGxYRHVwMWJaaG83ZUVTenRkVmxxNXhuTDdHdEN0cU9uClZxODZCeG54WUxPZGQxR2tySUhxNGc0RHpyaWNpb0lkcGFKM3REWTU5VzlpSzhvSnFQalFMWjQ5em1YZTgzcWcKbUo4dFMwRXhpVkFSY05Mb2xUcHlzKzlDVStQdE5ZcWNQa3dadFYwQ1F2ZjR2TlNZN1RNaVlaWWd6VkVMQVpsMApoNGJ4dFJLcjBNcytJTzFlcmZFNStJRTB3QjlFVC83d2MzRy8raWg2STZaM1g0YlgvQStqL001MmVkL0t0V25SCmRjTTdMV0RjY1JXczl5c1hlT1M3SnVxZHJ3Q1lQQ2RISHQrMy9WVHcKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="

export INPUT_DB_EP1="az-a.hyundb0203.3c598fbfdcb4453690aa1111f12f59f6.mysql.managed-service.kr-central-2.kakaocloud.com"
export INPUT_DB_EP2="az-b.hyundb0203.3c598fbfdcb4453690aa1111f12f59f6.mysql.managed-service.kr-central-2.kakaocloud.com"

DB_EP1=$(echo -n "$INPUT_DB_EP1" | base64 -w 0)
DB_EP2=$(echo -n "$INPUT_DB_EP2" | base64 -w 0)

sudo tee -a /etc/environment << EOF
export JAVA_VERSION="17"
export SPRING_BOOT_VERSION="3.1.0"
export DOCKER_IMAGE_NAME="demo-spring-boot"
export DOCKER_JAVA_VERSION="17-jdk-slim"
EOF

source /etc/environment

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

sudo wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O /usr/local/bin/kic-iam-auth
sudo chmod +x /usr/local/bin/kic-iam-auth


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


