#!/bin/bash
# hadoop_init.sh
sleep 600
set -e

# 스크립트 다운로드 사이트 유효성 검사
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day2/Lab03/hadoop-init.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }

# 스크립트 다운로드 후 실행
wget https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day2/Lab03/hadoop-init.sh
chmod +x tg_full_setup.sh
sudo -E ./tg_full_setup.sh
