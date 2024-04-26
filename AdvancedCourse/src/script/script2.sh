#!/bin/bash

sudo apt-get install -y openjdk-17-jdk maven || { echo "kakaocloud: Failed to install openjdk-17-jdk and maven"; exit 1; }
sudo apt install tree || { echo "kakaocloud: Failed to install tree"; exit 1; }
echo "kakaocloud: Additional software installation completed"


echo "kakaocloud: 12.Setting .kube/config"
sudo mkdir /home/ubuntu/.kube || { echo "kakaocloud: Failed to create .kube directory"; exit 1; }
sudo cp /home/ubuntu/tutorial/AdvancedCourse/src/manifests/kube-config.yaml /home/ubuntu/.kube/config || { echo "kakaocloud: Failed to set kube-config.yaml"; exit 1; }
envsubst < /home/ubuntu/.kube/config > /home/ubuntu/.kube/config.tmp && mv /home/ubuntu/.kube/config.tmp /home/ubuntu/.kube/config || { echo "kakaocloud: Failed to modify /home/ubuntu/.kube/config"; exit 1; }
sudo chmod 600 /home/ubuntu/.kube/config || { echo "kakaocloud: Failed to change permission of /home/ubuntu/.kube/config"; exit 1; }
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config || { echo "kakaocloud: Failed to change ownership of /home/ubuntu/.kube/config"; exit 1; }
echo "kakaocloud: Setting .kube/config completed"


echo "kakaocloud: 13.Downloading helm-values.yaml and applying environment substitutions"
sudo cp /home/ubuntu/tutorial/AdvancedCourse/src/manifests/helm-values.yaml /home/ubuntu/values.yaml || { echo "kakaocloud: Failed to download helm-values.yaml"; exit 1; }
envsubst < /home/ubuntu/yaml/lab6-manifests.yaml > /home/ubuntu/yaml/manifests.tmp && mv /home/ubuntu/yaml/manifests.tmp /home/ubuntu/yaml/lab6-manifests.yaml || { echo "kakaocloud: Failed to modify /home/ubuntu/yaml/lab6-manifests.yaml"; exit 1; }
envsubst < /home/ubuntu/values.yaml > /home/ubuntu/values.tmp && mv /home/ubuntu/values.tmp /home/ubuntu/values.yaml || { echo "kakaocloud: Failed to modify /home/ubuntu/values.yaml"; exit 1; }
echo "kakaocloud: Environment substitutions applied and setup completed"

echo "kakaocloud: 14.Checking Kubernetes cluster nodes status"
kubeconfig="/home/ubuntu/.kube/config"
KUBECONFIG=$kubeconfig kubectl get nodes || { echo "kakaocloud: Failed to communicate with Kubernetes cluster"; exit 1; }
echo "kakaocloud: Successfully communicated with Kubernetes cluster"
