#!/bin/bash


echo "kakaocloud: section_4"

echo "kakaocloud: Setting up .kube directory and configuration file"

sudo mkdir /home/ubuntu/.kube || { echo "Failed to create .kube directory"; exit 1; }

sudo curl -o /home/ubuntu/.kube/config https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/AdvancedCourse/src/manifests/kube-config.yaml || { echo "Failed to download kube-config.yaml"; exit 1; }

echo "kakaocloud: .kube setup completed"
