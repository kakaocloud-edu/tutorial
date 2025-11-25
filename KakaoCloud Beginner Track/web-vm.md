# 실습 가이드

이 문서는 실습 교재의 페이지 번호 흐름에 맞춰 명령어를 순서대로 실행할 수 있도록 구성되었습니다.

---

## 1. 간단한 웹페이지 띄우기

### 106p - 1
패키지 목록을 최신 상태로 업데이트합니다.
```bash
sudo apt update
```

### 106p - 2
Nginx 웹 서버를 설치합니다.
```bash
sudo apt install nginx -y
```

### 107
Nginx 서비스가 정상적으로 실행 중인지 상태를 확인합니다.
```bash
sudo systemctl status nginx
```

### 109
Nginx 서비스를 시작합니다.
```bash
sudo systemctl start nginx
```

### 110
Nginx 웹 루트 디렉터리를 생성합니다.
```bash
sudo mkdir –p /var/www/nginx
```

### 111
테스트용 index.html 파일을 생성합니다.
```bash
echo '<!DOCTYPE html>
<html>
  <head>
    <title>Hello from Nginx</title>
  </head>
  <body>
    <h1>Hello, Kakao Cloud!</h1>
    <p>This page is served by Nginx</p>
  </body>
</html>' | sudo tee /var/www/nginx/index.html
```

### 112 - 1
웹 디렉터리의 권한을 755로 설정합니다.
```bash
sudo chmod 755 /var/www/nginx
```

### 112 - 2
index.html 파일의 권한을 644로 설정합니다.
```bash
sudo chmod 644 /var/www/nginx/index.html
```

### 114
Nginx 서버 설정을 작성합니다 (포트 8080).
```bash
sudo tee /etc/nginx/sites-available/default >/dev/null <<'EOF'
server {
    listen 8080 default_server;
    listen [::]:8080 default_server;

    root /var/www/nginx;
    index index.html index.htm;

    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF
```

### 115 - 1
Nginx 설정 파일의 문법 오류를 검사합니다.
```bash
sudo nginx -t
```

### 115 - 2
설정 적용을 위해 Nginx를 재시작합니다.
```bash
sudo systemctl restart nginx
```

### 116
재시작 후 Nginx 상태를 확인합니다.
```bash
sudo systemctl status nginx
```

### 118
localhost의 8080 포트로 접속하여 웹페이지를 확인합니다.
```bash
curl http://localhost:8080
```

### 119 - 1
패키지 목록을 다시 업데이트합니다.
```bash
sudo apt update
```

### 119 - 2
Apache2 웹 서버를 설치합니다.
```bash
sudo apt install apache2 -y
```

### 120
Apache2 서비스 상태를 확인합니다.
```bash
sudo systemctl status apache2
```

### 122
Apache 웹 루트 디렉터리를 생성합니다.
```bash
sudo mkdir -p /var/www/apache
```

### 123
Apache용 테스트 index.html 파일을 생성합니다.
```bash
echo '<!DOCTYPE html>
<html>
  <head>
    <title>Hello from Apache</title>
  </head>
  <body>
    <h1>Hello, Kakao Cloud!</h1>
    <p>This page is served by Apache</p>
  </body>
</html>' | sudo tee /var/www/apache/index.html
```

### 124 - 1
Apache 웹 디렉터리의 권한을 설정합니다.
```bash
sudo chmod 755 /var/www/apache
```

### 124 - 2
Apache index.html 파일의 권한을 설정합니다.
```bash
sudo chmod 644 /var/www/apache/index.html
```

### 125
Apache가 사용할 포트를 8081로 변경합니다.
```bash
sudo tee /etc/apache2/ports.conf >/dev/null <<'EOF'
Listen 8081

<IfModule ssl_module>
    Listen 443
</IfModule>

<IfModule mod_gnutls.c>
    Listen 443
</IfModule>
EOF
```

### 126
Apache 가상 호스트 설정을 작성합니다 (포트 8081).
```bash
sudo tee /etc/apache2/sites-available/000-default.conf >/dev/null <<'EOF'
<VirtualHost *:8081>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/apache

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF
```

### 127 - 1
Apache 설정 파일의 문법을 검사합니다.
```bash
sudo apache2ctl configtest
```

### 127 - 2
설정 적용을 위해 Apache를 재시작합니다.
```bash
sudo systemctl restart apache2
```

### 128
재시작 후 Apache 상태를 확인합니다.
```bash
sudo systemctl status apache2
```

### 130
localhost의 8081 포트로 접속하여 확인합니다.
```bash
curl http://localhost:8081
```

---

## 2. 트러블 슈팅

### 143 - 1
문제를 재현하기 위해 Nginx 서비스를 강제로 중지합니다.
```bash
sudo systemctl stop nginx
```

### 143 - 2
웹페이지 접속이 실패하는 것을 확인합니다.
```bash
curl http://localhost:8080
```

### 145
Nginx 서비스가 중지된 상태인지 확인합니다.
```bash
sudo systemctl status nginx
```

### 147 - 1
Nginx 서비스를 다시 시작하여 복구합니다.
```bash
sudo systemctl restart nginx
```

### 147 - 2
웹페이지 접속이 정상화되었는지 확인합니다.
```bash
curl http://localhost:8080
```

### 148
Nginx 서비스 상태를 확인합니다.
```bash
sudo systemctl status nginx
```

### 153
Nginx 포트를 80번으로 변경하여 포트 충돌을 유도합니다.
```bash
sudo tee /etc/nginx/sites-available/default >/dev/null <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/nginx;
    index index.html index.htm;

    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF
```

### 154
Nginx 설정 문법을 검사합니다.
```bash
sudo nginx -t
```

### 156
Apache 포트도 80번으로 변경하여 충돌을 유도합니다.
```bash
sudo tee /etc/apache2/ports.conf >/dev/null <<'EOF'
Listen 80

<IfModule ssl_module>
    Listen 443
</IfModule>

<IfModule mod_gnutls.c>
    Listen 443
</IfModule>
EOF
```

### 158
Apache 가상 호스트 설정도 80번 포트로 변경합니다.
```bash
sudo tee /etc/apache2/sites-available/000-default.conf >/dev/null <<'EOF'
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/apache

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOF
```

### 159 - 1
Apache 설정 문법을 검사합니다.
```bash
sudo apache2ctl configtest
```

### 159 - 2
Apache를 재시작하여 80번 포트를 선점하게 합니다.
```bash
sudo systemctl restart apache2
```

### 160
Nginx 재시작을 시도하여 실패하는 것을 확인합니다 (포트 충돌).
```bash
sudo systemctl restart nginx
```

### 161
Nginx 에러 로그에서 포트 충돌(Bind failed) 메시지를 확인합니다.
```bash
tail -n 10 /var/log/nginx/error.log
```

### 162 - 1
패키지 목록을 업데이트합니다.
```bash
sudo apt update
```

### 162 - 2
포트 확인을 위해 net-tools를 설치합니다.
```bash
sudo apt install net-tools -y
```

### 163
80번 포트를 사용 중인 프로세스를 확인합니다.
```bash
sudo netstat -tulnp | grep 80
```

### 165
Nginx 설정을 8080 포트로 원상 복구합니다.
```bash
sudo tee /etc/nginx/sites-available/default >/dev/null <<'EOF'
server {
    listen 8080 default_server;
    listen [::]:8080 default_server;

    root /var/www/nginx;
    index index.html index.htm;

    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }
}
EOF
```

### 166 - 1
Nginx 설정 문법을 검사합니다.
```bash
sudo nginx -t
```

### 166 - 2
Nginx를 재시작합니다.
```bash
sudo systemctl restart nginx
```

### 167
Nginx가 포트를 정상적으로 점유했는지 확인합니다.
```bash
sudo netstat -tulnp | grep nginx
```

### 168
Nginx 서비스 상태를 최종 확인합니다.
```bash
sudo systemctl status nginx
```

### 177
정상 접속을 확인합니다.
```bash
curl http://localhost:8080
```

### 184
index.html 파일을 다른 곳으로 이동시켜 404 에러를 유도합니다.
```bash
sudo mv /var/www/nginx/index.html /home/ubuntu
```

### 185
접속 시도 시 404 Not Found 에러를 확인합니다.
```bash
curl http://localhost:8080
```

### 187
에러 로그를 확인하여 파일을 찾을 수 없음을 확인합니다.
```bash
tail -n 10 /var/log/nginx/error.log
```

### 188 - 1
설정 파일에서 root 경로를 확인합니다.
```bash
cat /etc/nginx/sites-available/default | grep root
```

### 188 - 2
파일을 원래 위치로 복구합니다.
```bash
sudo mv /home/ubuntu/index.html /var/www/nginx/
```

### 189
접속이 정상화되었는지 확인합니다.
```bash
curl http://localhost:8080
```

### 193
설정 파일에 오타(htp)를 넣어 문법 오류를 유발합니다.
```bash
sudo tee /etc/nginx/nginx.conf >/dev/null <<'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
}

htp {   # <- 의도적으로 'http' 오타
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF
```

### 194
Nginx 재시작을 시도하여 실패를 확인합니다.
```bash
sudo systemctl restart nginx
```

### 195
에러 로그에서 문법 오류 내용을 확인합니다.
```bash
tail -n 10 /var/log/nginx/error.log
```

### 196
설정 파일 문법 검사를 통해 오류 위치를 확인합니다.
```bash
sudo nginx -t
```

### 199
설정 파일의 오타를 수정하여 복구합니다.
```bash
sudo tee /etc/nginx/nginx.conf >/dev/null <<'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF
```

### 200 - 1
수정 후 문법 검사를 수행합니다.
```bash
sudo nginx -t
```

### 200 - 2
Nginx를 재시작합니다.
```bash
sudo systemctl restart nginx
```

### 201
Nginx 서비스 상태를 확인합니다.
```bash
sudo systemctl status nginx
```

### 205
파일 권한을 600(소유자만 읽기)으로 변경하여 403 에러를 유도합니다.
```bash
sudo chmod 600 /var/www/nginx/index.html
```

### 206
접속 시도 시 403 Forbidden 에러를 확인합니다.
```bash
curl http://localhost:8080
```

### 208
에러 로그에서 권한 거부(Permission denied)를 확인합니다.
```bash
tail -n 10 /var/log/nginx/error.log
```

### 209
현재 파일 권한을 확인합니다.
```bash
ls -l /var/www/nginx/
```

### 210
파일 권한을 644(누구나 읽기 가능)로 복구합니다.
```bash
sudo chmod 644 /var/www/nginx/index.html
```

### 211
변경된 권한을 확인합니다.
```bash
ls -l /var/www/nginx/
```

### 212
정상 접속을 최종 확인합니다.
```bash
curl http://localhost:8080
```
