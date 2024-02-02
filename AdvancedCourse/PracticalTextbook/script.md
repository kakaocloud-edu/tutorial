# bastion 스크립트 명령 실패 시 수동으로 명령어 입력



  ```bash
export PROJECT_NAME="kakaocloud-test"
export ACC_KEY="98cd807afa0c4555baa67cfeab039ec3"
export SEC_KEY="1j8zie-QAgZ4U5gRN9IXFFlD8W6AxcN563lZL943RGIs8Yj1cXK85IndQ_b3h2SqamJAz-7ENnjiNPjV5DCwwg"
export API_SERVER="https://9ce75b66-3314-42d7-89ff-c841b7f340f7-public.ke.kr-central-2.kakaocloud.com:443"
export AUTH_DATA="LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM2akNDQWRLZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJME1ESXdNVEV3TlRneE1Gb1hEVE0wTURFeU9URXhNRE14TUZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBSnZjCmlVNSs5cTN5ZTMvV1M0aUFxTVFQK3dSQjBPdHF0dnJIYU9LVko0WFdTc1lBejNWT0xDcGU3bkY4bWxuWExHeDkKWU5xVmZPOGUzZHFQZnJqa0RMc3lrTGJVRGJ5Sy84SWRuR0ZGOERqYm9mODAra2IyL0dFQzV0T3BPcjhpdDFUMApBZ3RGbzNMdHNUMjNTaGhycHFRU1dPVnoxdFVlZjQyWTYwR01hbE4xWG5jRDgxZHhadG5hbXh5UXIwdzI4Rm1MClUvcExxblBtWlk2b21vS0h1eTJ6MVJzZmZXOUJvY2JrKzRPSXVQSGNLTEgwcTJRYyt0Nlkza3BZWllYeFZEYTEKWFZkdjZtTU5LamUvWkc4bEFtazB2bXJYcldzeW9wdWlhdzhINnJBRjVONndjS0ZoNWJ0UUh0TEJTOXZzUUF0QwppOXNtSHpWNHpCNGNpdkdtU3FzQ0F3RUFBYU5GTUVNd0RnWURWUjBQQVFIL0JBUURBZ0trTUJJR0ExVWRFd0VCCi93UUlNQVlCQWY4Q0FRQXdIUVlEVlIwT0JCWUVGTTZHRlN6R1NOQWRLbmpNc0xBNGtsQVJtaFcvTUEwR0NTcUcKU0liM0RRRUJDd1VBQTRJQkFRQndpTkRueXFJOHk3b3FYaWZRZmxXQlYvQ1NiSlJueVpYUW1mNDM1bUx5WWI0TQpiSytPL3RnWWVEWDUrSmRsQ3RHNGpDTWhqQnFCNTFuWUxseU5lc1RJMXZIcUV0UGhtdTlhNWp2bVc3VjBzbldnCmVmWnR4OFlFc2lxTUttdmUvalRtM2ViZ2d1S1JWZEFRNEpGanFucUNxaStXSmFDR2FjOXFxcExaUlN1eXJGWGgKZkhZUC9Tc0ZiM1dmNFFUUGVLSWQyWXhzRXZ5VU9MK1Rra1ZCckZnOWo5eE5MRHhDak44ZFVia1cxdlQwbHFOcgpjbkpRZXhEZjB3QlVHdEVvb1ByZXU5WG5Ma0R1NHduWFFhM0kzdkFZWHNLUm1iODRpTHdZZlVyWUFycUo2UDBKCjd0Y3JtNU5DWUJISEtaRFo5cTc3SzIvUFl6TjhFeGZqM2Mxei8yS0YKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo="

export INPUT_DB_EP1="az-b.database-hyun.fe214376ac7e402590083b76d98ff5f5.mysql.managed-service.kr-central-2.kakaocloud.com"
export INPUT_DB_EP2="az-a.database-hyun.fe214376ac7e402590083b76d98ff5f5.mysql.managed-service.kr-central-2.kakaocloud.com"

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

curl -sSL -o /home/ubuntu/yaml/lab6-Secret.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/lab6-Secret.yaml

curl -sSL -o /home/ubuntu/yaml/lab6-Deployment.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/lab6-Deployment.yaml

curl -sSL -o /home/ubuntu/yaml/lab6-ConfigMapDB.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/lab6-ConfigMapDB.yaml

sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

sudo mkdir /home/ubuntu/.kube

curl -sSL -o /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/config.yaml

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

curl -sSL -o /home/ubuntu/yaml/values.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/script/values.yaml

```
