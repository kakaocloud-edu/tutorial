#!/bin/bash


echo "kakaocloud: section_5"

echo "kakaocloud: Installing kic-iam-auth"

sudo wget https://objectstorage.kr-central-1.kakaoi.io/v1/9093ef2db68545b2bddac0076500b448/kc-docs/docs%2Fbinaries-kic-iam-auth%2FLinux%20x86_64%2064Bit%2Fkic-iam-auth -O kic-iam-auth || { echo "Failed to download kic-iam-auth"; exit 1; }

sudo chmod +x kic-iam-auth || { echo "Failed to change permission of kic-iam-auth"; exit 1; }

sudo mv kic-iam-auth /usr/local/bin/ || { echo "Failed to move kic-iam-auth to /usr/local/bin/"; exit 1; }

echo "kakaocloud: kic-iam-auth installation completed"
