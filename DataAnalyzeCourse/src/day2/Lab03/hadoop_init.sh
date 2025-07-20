#!/bin/bash
# hadoop_init.sh
sleep 600
set -e  # 오류 발생 시 스크립트 종료

echo "kakaocloud: 스크립트 다운로드 사이트 유효성 검사 시작"
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day2/Lab03/hadoop-init.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }

wget https://github.com/kakaocloud-edu/tutorial/raw/refs/heads/main/DataAnalyzeCourse/src/day2/Lab03/hadoop-init.sh
chmod +x tg_full_setup.sh
sudo -E ./tg_full_setup.sh
