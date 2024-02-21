#!/bin/bash

echo "kakaocloud: section_2"

echo "kakaocloud: Downloading YAML files"

sudo wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/manifests/lab6Yaml.tar -O /home/ubuntu/yaml/lab6Yaml.tar || { echo "kakaocloud: Failed to download lab6Yaml.tar"; exit 1; }

sudo curl -o /home/ubuntu/yaml/lab6-Secret.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-Secret.yaml || { echo "kakaocloud: Failed to download lab6-Secret.yaml"; exit 1; }

sudo curl -o /home/ubuntu/yaml/lab6-Deployment.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-Deployment.yaml || { echo "kakaocloud: Failed to download lab6-Deployment.yaml"; exit 1; }

sudo curl -o /home/ubuntu/yaml/lab6-ConfigMapDB.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/lab6-ConfigMapDB.yaml || { echo "kakaocloud: Failed to download lab6-ConfigMapDB.yaml"; exit 1; }

echo "kakaocloud: All YAML files downloaded"
