
#!/bin/bash

# 출력 메시지와 함께 실행 상태를 확인하는 함수
function log_and_exit {
    echo "kakaocloud: $1"; exit 1;
}

# 디렉터리를 만들고 권한을 설정하는 함수
function prepare_directory {
    if [ ! -d "$1" ]; then
        sudo mkdir -p "$1" && sudo chmod 777 "$1" || log_and_exit "Failed to create or set permissions for directory $1."
    fi
}

# 파일을 복사하는 함수
function copy_file {
    if [ ! -f "$2" ]; then
        sudo cp "$1" "$2" || log_and_exit "Failed to copy file from $1 to $2."
    fi
}

# 파일 또는 디렉터리의 존재 여부를 확인하는 함수
function check_exist_and_set {
    if [ ! -e "$2" ]; then
        sudo "$1" "$2" || log_and_exit "Failed to set $3 for $2."
    fi
}

# 필수 환경변수 확인
echo "kakaocloud: 3.Variables validity test start"
required_variables=(
    ACC_KEY SEC_KEY EMAIL_ADDRESS CLUSTER_NAME API_SERVER AUTH_DATA PROJECT_NAME
    INPUT_DB_EP1 INPUT_DB_EP2 DOCKER_IMAGE_NAME DOCKER_JAVA_VERSION JAVA_VERSION
    SPRING_BOOT_VERSION DB_EP1 DB_EP2
)
for var in "${required_variables[@]}"; do
    [[ -z "${!var}" ]] && log_and_exit "필수 환경변수 $var 가 설정되지 않았습니다. 스크립트를 종료합니다."
done
echo "kakaocloud: Variables are valid"

# GitHub 연결 테스트
echo "kakaocloud: 4.Github Connection test start"
curl --output /dev/null --silent --head --fail "https://github.com" || log_and_exit "Github Connection failed"
echo "kakaocloud: Github Connection succeeded"

# 디렉터리 준비
echo "kakaocloud: 5.Preparing directories and files"
prepare_directory "/home/ubuntu/yaml"
echo "kakaocloud: Directories prepared"

# YAML 파일 다운로드
echo "kakaocloud: 6.Downloading YAML files"
if [ ! -d "/home/ubuntu/tutorial" ]; then
    sudo git clone https://github.com/kakaocloud-edu/tutorial.git /home/ubuntu/tutorial || log_and_exit "Failed to git clone"
fi
copy_file "/home/ubuntu/tutorial/AdvancedCourse/src/manifests/lab6-*" "/home/ubuntu/yaml"
echo "kakaocloud: All YAML files downloaded"

# Spring 디렉터리 준비
echo "kakaocloud: 7.Preparing Spring directories and files"
copy_file "/home/ubuntu/tutorial/AdvancedCourse/src/spring" "/home/ubuntu/"
check_exist_and_set "chmod +x" "/home/ubuntu/spring/mvnw" "executable permission"
echo "kakaocloud: Spring Directories and files prepared"

# kubectl 설치
echo "kakaocloud: 8.Installing kubectl"
if [ ! -f "/usr/local/bin/kubectl" ]; then
    sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" || log_and_exit "Failed to download kubectl binary"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl || log_and_exit "Failed to install kubectl binary"
fi
echo "kakaocloud: Kubectl installed"

# 기타 설정
# 이후 단계들도 위와 비슷하게 작업을 진행합니다.
