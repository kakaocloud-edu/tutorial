#!/bin/bash


echo "kakaocloud: section_3"

echo "kakaocloud: Installing kubectl"

sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" || { echo "kakaocloud: Failed to download kubectl binary"; exit 1; }

sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl || { echo "kakaocloud: Failed to install kubectl binary"; exit 1; }

echo "kakaocloud: kubectl installed"

