#!/bin/bash

echo "kakaocloud: section_7"
echo "kakaocloud: Installing additional software"
sudo apt install unzip || { echo "Failed to install unzip"; exit 1; }
sudo apt-get install -y openjdk-17-jdk maven || { echo "Failed to install openjdk-17-jdk and maven"; exit 1; }
echo "kakaocloud: Additional software installation completed"
