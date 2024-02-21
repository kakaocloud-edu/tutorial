#!/bin/bash

echo "kakaocloud: section_6"
echo "kakaocloud: Installing Docker and setting it up"
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg || { echo "Failed to download Docker GPG key"; exit 1; }
sudo echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null || { echo "Failed to add Docker repository to sources.list"; exit 1; }
sudo apt-get update || { echo "Failed to update apt repository"; exit 1; }
sudo apt-get install -y docker-ce docker-ce-cli containerd.io || { echo "Failed to install Docker"; exit 1; }
sudo chmod 666 /var/run/docker.sock || { echo "Failed to change permission of docker.sock"; exit 1; }
echo "kakaocloud: Docker installation and setup completed"
