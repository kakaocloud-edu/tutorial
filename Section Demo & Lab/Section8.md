# [Demo] GPU 생성 및 JupyterNotebook 실습

인스턴스는 가상화된 하드웨어 리소스로 다양한 인스턴스 유형의 서버를 구성합니다.GPU 서비스에서 인스턴스를 생성하는 방법은 다음과 같습니다.

1. GPU 인스턴스 만들기
    - 이름 및 개수 : gpu-instance / 1개
    - Image : Ubuntu 20.04 (GPU)
    - Instance 타입 : p2i.6xlarge
    - Root Volume : 50GB
    - VPC : 172.16.0.0/16
    - Subnet : 172.16.0.0/20
    - Security Group
        - Inbound : TCP, ${나의 공인IP}/32, 22
        - Inbound : TCP, ${나의 공인IP}/32, 8080
        - Outbound : ALL, 0.0.0./0. ALL
2. 사용자 스크립트에 아래 스크립트를 넣기
    ```bash
    #!/bin/bash

    echo "kakaocloud: 1. Download the cuda-keyring package"
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
    echo "Downloaded cuda-keyring package"
    
    echo "kakaocloud: 2. Install the cuda-keyring package"
    dpkg -i cuda-keyring_1.1-1_all.deb
    echo "Installed cuda-keyring package"
    
    echo "kakaocloud: 3. apt-get update"
    apt-get update
    echo "Updated apt-get"
    
    echo "kakaocloud: 4. Install cuDNN"
    apt-get install cudnn-cuda-12 -y
    echo "Installed cuDNN"
    
    echo "kakaocloud: 5. Check version of cuDNN"
    CUDNN_MAJOR=$(cat /usr/include/cudnn_version.h | grep '#define CUDNN_MAJOR' | awk '{print $3}')
    echo "CUDNN_MAJOR version is: $CUDNN_MAJOR"
    
    echo "kakaocloud: 6. Install python3.8"
    apt-get install python3.8 -y
    apt-get install python3.8-venv -y
    apt-get install python3.8-dev -y
    apt-get install python3-pip -y
    echo "Installed Python 3.8 and related packages"
    
    echo "kakaocloud: 7. Create python virtual environment"
    python3.8 -m venv jupyter_env
    echo "Created python virtual environment"
    
    echo "kakaocloud: 8. Activate virtual environment"
    source jupyter_env/bin/activate
    echo "Activated virtual environment"
    
    echo "kakaocloud: 9. Upgrade pip"
    pip install --upgrade pip
    echo "Upgraded pip"
    
    echo "kakaocloud: 10. Install Jupyter"
    pip install jupyter jupyter_server
    echo "Installed Jupyter"
    
    echo "kakaocloud: 11. Generate Jupyter notebook configuration"
    #/home/ubuntu/.jupyter/jupyter_server_config.py
    jupyter notebook --generate-config
    echo "Generated Jupyter notebook configuration"
    
    echo "kakaocloud: 12. Set password for Jupyter Notebook"
    PASSWORD="admin"
    HASHED_PASSWORD=$(python3.8 -c "from jupyter_server.auth import passwd; print(passwd('$PASSWORD'))")
    echo "Password hashed"
    
    echo "kakaocloud: 13. Add hashed password to Jupyter configuration"
    JUPYTER_CONFIG_DIR=$(jupyter --config-dir)
    JUPYTER_CONFIG_FILE="$JUPYTER_CONFIG_DIR/jupyter_server_config.py"
    echo "c.ServerApp.password = u'$HASHED_PASSWORD'" >> $JUPYTER_CONFIG_FILE
    echo "Added hashed password to Jupyter configuration"
    
    echo "kakaocloud: 14. Start Jupyter Notebook"
    jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser --allow-root &
    echo "Started Jupyter Notebook"
    ```
3. 배포판 정보 확인
    - /etc/ 디렉토리 내의 *release 패턴과 일치하는 모든 파일의 내용을 출력
    ```bash
    cat /etc/*release
    ```
    ```bash
    lsb_release -a
    ```
4. NVIDIA GPU 확인
    ```bash
    lspci | grep -i nvidia
    ```
    ```bash
    nvidia-smi
    ```
6. CUDA Toolkit 확인
    ```bash
    nvcc -V
    ```
7. cuDNN 다운로드 방법
   - https://developer.nvidia.com/cudnn-downloads
8. ssh로 GPU 인스턴스 접속
9. 관리자 계정으로 전환
    ```bash
    sudo -i
    ```
10. 현재 경로 파일 목록 확인
    ```bash
    ls
    ```
11. Python 가상 환경을 활성화
    ```bash
    source jupyter_env/bin/activate
    ```
12. Jupyter 서버의 설정 파일 내용을 출력
    ```bash
    cat .jupyter/jupyter_server_config.py
    ```
13. 현재 실행 중인 Jupyter 관련 프로세스를 검색
    ```bash
    ps aux | grep jupyter
    ```
14. GPU 인스턴스의 공인 IP:8080으로 접속
