#!/bin/bash

echo "kakaocloud: section_9"
echo "kakaocloud: Downloading helm-values.yaml and applying environment substitutions"
sudo curl -o /home/ubuntu/values.yaml https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/helm-values.yaml || { echo "Failed to download helm-values.yaml"; exit 1; }

sudo envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config || { echo "Failed to modify /home/ubuntu/.kube/config"; exit 1; }

sudo envsubst < /home/ubuntu/yaml/lab6-Deployment.yaml > /home/ubuntu/yaml/deploy.tmp && mv /home/ubuntu/yaml/deploy.tmp /home/ubuntu/yaml/lab6-Deployment.yaml || { echo "Failed to modify /home/ubuntu/yaml/lab6-Deployment.yaml"; exit 1; }

sudo envsubst < /home/ubuntu/yaml/lab6-Secret.yaml > /home/ubuntu/yaml/secret.tmp && mv /home/ubuntu/yaml/secret.tmp /home/ubuntu/yaml/lab6-Secret.yaml || { echo "Failed to modify /home/ubuntu/yaml/lab6-Secret.yaml"; exit 1; }

sudo envsubst < /home/ubuntu/values.yaml > /home/ubuntu/values.tmp && mv /home/ubuntu/values.tmp /home/ubuntu/values.yaml || { echo "Failed to modify /home/ubuntu/values.yaml"; exit 1; }
echo "kakaocloud: Environment substitutions applied and setup completed"
