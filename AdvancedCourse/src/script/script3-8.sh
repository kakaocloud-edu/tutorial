#!/bin/bash

echo "kakaocloud: section_8"
echo "kakaocloud: Setting permissions for .kube/config"
sudo chmod 600 /home/ubuntu/.kube/config || { echo "Failed to change permission of /home/ubuntu/.kube/config"; exit 1; }
sudo chown ubuntu:ubuntu /home/ubuntu/.kube/config || { echo "Failed to change ownership of /home/ubuntu/.kube/config"; exit 1; }
echo "kakaocloud: Permissions set for .kube/config"
