#!/bin/bash

chmod 600 /home/ubuntu/.kube/config
chown ubuntu:ubuntu /home/ubuntu/.kube/config

sudo awk -v auth_data="${AUTH_DATA}" '{while(match($0,/\$\{AUTH_DATA\}/)) { $0 = substr($0, 1, RSTART-1) auth_data substr($0, RSTART+RLENGTH)}; print}' /home/ubuntu/.kube/config > /tmp/temp_config && sudo mv /tmp/temp_config /home/ubuntu/.kube/config
sudo sed -i "s|\${API_SERVER}|$API_SERVER|g" /home/ubuntu/.kube/config
sudo sed -i "s|\${ACC_KEY}|$ACC_KEY|g" /home/ubuntu/.kube/config
sudo sed -i "s|\${SEC_KEY}|$SEC_KEY|g" /home/ubuntu/.kube/config
sudo sed -i "s|\${CLUSTER_NAME}|$CLUSTER_NAME|g" /home/ubuntu/.kube/config
sudo sed -i "s|\${PROJECT_NAME}|$PROJECT_NAME|g" /home/ubuntu/yaml/lab6-Deployment.yaml
sudo sed -i "s|\${DOCKER_IMAGE_NAME}|$DOCKER_IMAGE_NAME|g" /home/ubuntu/yaml/lab6-Deployment.yaml
sudo sed -i "s|\${DB_EP1}|$DB_EP1|g" /home/ubuntu/yaml/lab6-Secret.yaml
sudo sed -i "s|\${DB_EP2}|$DB_EP2|g" /home/ubuntu/yaml/lab6-Secret.yaml
sudo sed -i "s|\${PROJECT_NAME}|$PROJECT_NAME|g" /home/ubuntu/yaml/values.yaml
sudo sed -i "s|\${INPUT_DB_EP1}|$INPUT_DB_EP1|g" /home/ubuntu/yaml/values.yaml
sudo sed -i "s|\${INPUT_DB_EP2}|$INPUT_DB_EP2|g" /home/ubuntu/yaml/values.yaml
sudo sed -i "s|\${DOCKER_IMAGE_NAME}|$DOCKER_IMAGE_NAME|g" /home/ubuntu/yaml/values.yaml

