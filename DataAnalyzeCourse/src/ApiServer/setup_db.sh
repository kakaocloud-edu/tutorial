#!/bin/bash

# 환경변수 설정(필요한 경우)
# 실제 환경에 맞게 수정 가능
MYSQL_USER="${MYSQL_USER:-admin}"
MYSQL_PASS="${MYSQL_PASS:-admin1234}"
source /home/ubuntu/.bashrc

# MySQL 포트 체크 (선택사항)
if ! timeout 3 bash -c "</dev/tcp/$MYSQL_HOST/3306" 2>/dev/null; then
  echo "MySQL이 $MYSQL_HOST:3306 에서 응답하지 않습니다."
  exit 1
fi

# 초기 스키마 및 데이터 설정용 SQL을 HERE DOC으로 직접 포함
SQL_COMMANDS=$(cat <<'EOF'
DROP DATABASE IF EXISTS shopdb;
CREATE DATABASE shopdb;
USE shopdb;

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    gender CHAR(1),
    age INT
);

CREATE TABLE IF NOT EXISTS users_logs (
    history_id INT AUTO_INCREMENT PRIMARY KEY,        -- 고유 이력 ID
    user_id VARCHAR(36),                              -- 사용자 ID
    event_type ENUM('CREATED', 'DELETED') NOT NULL,   -- 이벤트 유형 ('생성' 또는 '삭제')
    event_time DATETIME DEFAULT CURRENT_TIMESTAMP     -- 이벤트 발생 시간
);


INSERT INTO users (user_id, name, email, gender, age) VALUES
('u1','Alice','alice@example.com','F',30),
('u2','Bob','bob@example.com','M',20),
('u3','Charlie','charlie@example.com','M',40),
('u4','Diana','diana@example.com','F',25);

CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    price DECIMAL(10,2),
    category VARCHAR(100)
);
INSERT INTO products (id, name, price, category) VALUES
('101', 'Wireless Earbuds', 79.99, 'Electronics'),
('102', 'Bluetooth Speaker', 49.99, 'Electronics'),
('103', 'Sneakers', 59.99, 'Fashion'),
('104', 'Backpack', 39.99, 'Fashion'),
('105', 'Coffee Mug', 9.99, 'Home'),
('106', 'Gaming Mouse', 29.99, 'Electronics'),
('107', 'Sunglasses', 19.99, 'Fashion'),
('108', 'Laptop Stand', 25.00, 'Electronics'),
('109', 'Gaming Keyboard', 89.99, 'Gaming'),
('110', 'Game Console', 299.00, 'Gaming'),
('111', 'Python Programming Book', 35.00, 'Books'),
('112', 'Science Fiction Novel', 12.99, 'Books'),
('113', 'Fashionable Hat', 15.99, 'Fashion'),
('114', 'Air Fryer', 79.00, 'Home'),
('115', 'Vacuum Cleaner', 99.99, 'Home'),
('116', 'Coffee Machine', 129.99, 'Home'),
('117', 'Jeans', 49.99, 'Fashion'),
('118', 'Smartphone', 699.99, 'Electronics'),
('119', 'Tablet', 399.99, 'Electronics'),
('120', 'Dress', 59.99, 'Fashion'),
('121', 'Gaming Headset', 59.99, 'Gaming'),
('122', 'Cookbook', 24.99, 'Books'),
('123', 'Thriller Novel', 14.99, 'Books'),
('124', 'T-Shirt', 19.99, 'Fashion');

CREATE TABLE IF NOT EXISTS sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    login_time DATETIME DEFAULT NULL,
    logout_time DATETIME DEFAULT NULL,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(36) PRIMARY KEY,    -- 고유 리뷰 ID
    user_id VARCHAR(36),                  -- 사용자 ID
    session_id VARCHAR(36),               -- 세션 ID
    product_id VARCHAR(10),               -- 리뷰 대상 상품 ID
    rating INT,                           -- 리뷰 점수
    review_time DATETIME,                 -- 리뷰 작성 시간
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(36) PRIMARY KEY,      -- 고유 주문 ID
    user_id VARCHAR(36),                  -- 사용자 ID
    session_id VARCHAR(36),               -- 세션 ID
    product_id VARCHAR(10),               -- 주문한 상품 ID
    price DECIMAL(10,2),                  -- 주문 가격 (단가)
    quantity INT DEFAULT 1,               -- 주문 수량
    order_time DATETIME,                  -- 주문 시간
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS search_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36),
    search_query VARCHAR(255),
    searched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,         -- 고유 장바구니 항목 ID
    session_id VARCHAR(36),                         -- 세션 ID
    user_id VARCHAR(36),                            -- 사용자 ID
    product_id VARCHAR(10),                         -- 상품 ID
    quantity INT DEFAULT 1,                         -- 수량
    price DECIMAL(10,2),                            -- 상품 가격 (단가, 장바구니에 추가 시점 기준)
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,    -- 추가 시간
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 마지막 수정 시간
    FOREIGN KEY (session_id) REFERENCES sessions(session_id), -- 세션 참조
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,          -- 사용자 참조
    FOREIGN KEY (product_id) REFERENCES products(id)          -- 상품 참조
);

CREATE TABLE IF NOT EXISTS cart_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,           -- 고유 로그 ID
    cart_id INT,                                     -- 참조된 장바구니 항목 ID (필요시 저장)
    session_id VARCHAR(36),                          -- 세션 ID
    user_id VARCHAR(36),                             -- 사용자 ID
    product_id VARCHAR(10),                          -- 상품 ID
    old_quantity INT DEFAULT 0,          -- 변경 전 수량 (0일 수 있음)
    new_quantity INT DEFAULT 0,          -- 변경 후 수량 (0 이상)
    price DECIMAL(10,2),                             -- 상품 가격 (단가)
    event_type ENUM('ADDED', 'UPDATED', 'REMOVED', 'CHECKED_OUT'),
    event_time DATETIME DEFAULT CURRENT_TIMESTAMP,   -- 이벤트 발생 시간
    FOREIGN KEY (session_id) REFERENCES sessions(session_id), -- 세션 참조
    FOREIGN KEY (product_id) REFERENCES products(id) -- 상품 참조
);


SELECT 'Database and initial setup completed.' AS message;
EOF
)

echo "MySQL에 초기 스키마 및 데이터 세팅 중..."
echo "$SQL_COMMANDS" | mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASS"
if [ $? -eq 0 ]; then
    echo "DB 초기 세팅 완료."
else
    echo "DB 초기 세팅 실패."
    exit 1
fi
