#!/bin/bash

echo "MYSQL_HOST set to: $MYSQL_HOST"
source /home/ubuntu/.bashrc

# 전역 변수 초기화
LOG_PREFIX="kakaocloud: "
LOG_COUNTER=0

# 로깅 함수 정의
log() {
    LOG_COUNTER=$((LOG_COUNTER + 1))
    echo "${LOG_PREFIX}${LOG_COUNTER}. $1"
}

# 명령 실행 및 상태 확인 함수
run_command() {
    "$@"
    if [ $? -eq 0 ]; then
        log "$1 succeeded."
    else
        log "Error: $1 failed."
        exit 1
    fi
}

# 1. 시스템 업데이트 및 필요한 패키지 설치
log "Updating system and installing Python, Gunicorn, and Nginx..."
run_command apt update
run_command apt install -y python3 python3-pip gunicorn nginx python3-mysql.connector mysql-client

# 2. Flask 설치
log "Installing Flask..."
run_command apt install -y python3-flask

# 3. Flask 애플리케이션 설정
APP_DIR="/var/www/flask_app"
log "Setting up Flask application in $APP_DIR..."
run_command mkdir -p $APP_DIR

cat > $APP_DIR/app.py <<EOL
from flask import Flask, request, make_response
import uuid
import time
import random
import mysql.connector
from mysql.connector import Error
from flask import jsonify
from flask.json import JSONEncoder
from decimal import Decimal

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # 또는 str(obj)로 변환할 수도 있습니다.
        return super(CustomJSONEncoder, self).default(obj)

app = Flask(__name__)

app.json_encoder = CustomJSONEncoder


DB_CONFIG = {
    'user': 'admin',
    'password': 'admin1234',
    'host': '${MYSQL_HOST}',
    'database': 'shopdb',
    'ssl_disabled': True
    
}

@app.before_request
def update_last_active():
    session_id = request.cookies.get('session_id')
    if session_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sessions SET last_active = NOW() WHERE session_id = %s",
                (session_id,)
            )
            conn.commit()
        except Exception as e:
            print(f"Failed to update last_active: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)
    


def respond_html_or_json(data, html_renderer):
    """
    data: 파이썬 dict (JSON 형태로 직렬화할 원본)
    html_renderer: 콜백 함수(또는 HTML 템플릿 렌더링 결과 반환)
    
    - 브라우저(기본) → text/html 반환
    - API (Accept: application/json) → JSON 반환
    """
    accept_header = request.headers.get("Accept", "")

    if "application/json" in accept_header:
        # JSON을 원하는 경우
        return jsonify(data)
    else:
        # 그 외 (주로 브라우저)
        return html_renderer(data)


def get_or_create_session_id():
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        # 세션을 DB에 저장
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (session_id) VALUES (%s)",
                (session_id,)
            )
            conn.commit()
        except Exception as e:
            print(f"Failed to create session: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    return session_id
    
def create_session_id():
    session_id = str(uuid.uuid4())
    # 세션을 DB에 저장
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_id) VALUES (%s)",
            (session_id,)
        )
        conn.commit()
    except Exception as e:
        print(f"Failed to create session: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return session_id
    
    
@app.route('/')
def home():
    
    # 모든 엔드포인트를 링크와 상세 설명으로 나열
    endpoints = {
        "Home": {"url": "/", "description": "메인 페이지로 이동합니다."},
        "Products": {"url": "/products", "description": "상품 목록을 확인할 수 있습니다."},
        "Product Detail": {"url": "/product?id=101", "description": "특정 상품의 세부 정보를 확인합니다. 'id' 파라미터가 필요합니다."},
        "Search": {"url": "/search?query=Bluetooth", "description": "검색 기능을 제공합니다. 'query' 파라미터로 키워드를 입력하세요."},
        "Checkout History": {"url": "/checkout_history", "description": "사용자의 결제 내역을 확인합니다."},
        "Categories": {"url": "/categories", "description": "모든 카테고리의 목록을 확인합니다."},
        "Category": {"url": "/category?name=Electronics", "description": "특정 카테고리의 상품 목록을 확인합니다."},
        "View Cart": {"url": "/cart/view", "description": "현재 세션의 장바구니를 확인합니다."},
        "Trigger Error": {"url": "/error", "description": "오류를 발생시켜 테스트합니다."}
    }

    # HTML로 반환
    html = "<h1>Online Shopping Mall</h1><p>이 사이트는 쇼핑몰 데이터를 축적하기 위한 테스트 환경입니다.</p><hr><ul>"
    html += "<h2>Endpoints with Get Requests</h2>"
    for name, info in endpoints.items():
        html += f"<li><a href='{info['url']}'>{name}</a>: {info['description']}</li>"
   

    # POST 요청용 폼 추가
    html += """
    <h2>Endpoints with POST Requests</h2>
    
    <!-- Add User -->
    <h3>Register</h3>
    <p>새로운 사용자를 등록합니다.</p>
    <form action="/add_user" method="post">
        <label for="user_id">User ID:</label>
        <input type="text" id="user_id" name="user_id" value="test_user" required>
        <br>
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" value="Test User" required>
        <br>
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" value="test@example.com" required>
        <br>
        <label for="gender">Gender (F/M):</label>
        <input type="text" id="gender" name="gender" value="M" required>
        <br>
        <label for="age">Age:</label>
        <input type="number" id="age" name="age" value="30" required>
        <br>
        <button type="submit">Register</button>
    </form>
    
    
    <!-- Delete User -->
    <h3>Unregister</h3>
    <p>사용자를 삭제합니다.</p>
    <form action="/delete_user" method="post">
        <label for="delete_user_id">User ID:</label>
        <input type="text" id="delete_user_id" name="user_id" value="test_user" required>
        <br>
        <button type="submit">Unregister</button>
    </form>

    <!-- Login -->
    <h3>Login</h3>
    <p>사용자 ID를 입력하여 로그인합니다.</p>
    <form action="/login" method="post">
        <label for="user_id">User ID:</label>
        <input type="text" id="user_id" name="user_id" value="u1" required>
        <button type="submit">Login</button>
    </form>

    <!-- Logout -->
    <h3>Logout</h3>
    <p>현재 로그인한 사용자를 로그아웃합니다.</p>
    <form action="/logout" method="post">
        <button type="submit">Logout</button>
    </form>

    <!-- Add to Cart -->
    <h3>Add to Cart</h3>
    <p>상품 ID를 입력하여 장바구니에 추가합니다.</p>
    <form action="/cart/add" method="post">
        <label for="product_id">Product ID:</label>
        <input type="text" id="product_id" name="id" value="101" required>
        <label for="quantity">Quantity:</label>
        <input type="number" id="quantity" name="quantity" value="1" min="1" required>
        <button type="submit">Add to Cart</button>
    </form>
    
    
    <!-- Remove from Cart -->
    <h3>Remove from Cart</h3>
    <p>장바구니에서 특정 상품을 제거하거나 수량을 줄입니다.</p>
    <form action="/cart/remove" method="post">
        <label for="remove_product_id">Product ID:</label>
        <input type="text" id="remove_product_id" name="product_id" value="101" required>
        <label for="remove_quantity">Quantity to Remove:</label>
        <input type="number" id="remove_quantity" name="quantity" min="1" value="1" required>
        <button type="submit">Remove from Cart</button>
    </form>


    <!-- Checkout -->
    <h3>Checkout</h3>
    <p>장바구니에 있는 모든 상품을 결제합니다.</p>
    <form action="/checkout" method="post">
        <button type="submit">Checkout</button>
    </form>

    <!-- Add Review -->
    <h3>Add Review</h3>
    <p>상품에 대한 평점을 남깁니다.</p>
    <form action="/add_review" method="post">
        <label for="review_product_id">Product ID:</label>
        <input type="text" id="review_product_id" name="product_id" value="101" required>
        <br>
        <label for="rating">Rating (1-5):</label>
        <input type="number" id="rating" name="rating" value="5" min="1" max="5" required>
        <button type="submit">Add Review</button>
    </form>
    """
    
    resp = make_response(html)
    session_id = get_or_create_session_id()
    resp.set_cookie('session_id', session_id)
    return resp


messages_storage = []

@app.route('/push-subscription', methods=['POST'])
def push_subscription():
    """
    외부 Push Subscription 서비스가 메시지를 POST 방식으로 보낼 수 있음
    수신된 메시지는 JSON 형식으로 처리되며, 메모리에 저장
    """
    try:
        # Parse the incoming JSON payload
        data = request.get_json()

        if not data:
            return "Invalid data format. Expected JSON payload.", 400

        # Save the message into the in-memory storage
        messages_storage.append(data)

        # Log the received message
        print(f"Received message: {data}")

        return "Message received and stored successfully.", 200

    except Exception as e:
        print(f"Error while processing push message: {e}")
        return f"An error occurred: {e}", 500



@app.route('/push-messages', methods=['GET'])
def get_push_messages():
    """
    GET 방식으로 저장된 데이터를 JSON 형식으로 반환
    브라우저 또는 API 클라이언트에서 데이터를 확인
    """
    try:
        # Respond with all stored messages as JSON
        return jsonify({"messages": messages_storage}), 200

    except Exception as e:
        print(f"Error while retrieving messages: {e}")
        return f"An error occurred: {e}", 500
    
@app.route('/add_user', methods=['POST'])
def add_user():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    email = request.form.get('email')
    gender = request.form.get('gender')
    age = request.form.get('age')

    if not (user_id and name and email and gender and age):
        return "All fields are required: user_id, name, email, gender, age. <a href='/'>[Home]</a>", 400

    if gender not in ['F', 'M']:
        return "Gender must be 'F' or 'M'. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user_id already exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        existing_user = cursor.fetchone()
        if existing_user:
            return "User ID already exists. <a href='/'>[Home]</a>", 409

        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (user_id, name, email, gender, age) VALUES (%s, %s, %s, %s, %s)",
            (user_id, name, email, gender, age)
        )
        
        # Add entry to users_logs table
        cursor.execute(
            "INSERT INTO users_logs (user_id, event_type) VALUES (%s, 'CREATED')",
            (user_id,)
        )
        
        conn.commit()
        return f"User {name} added successfully. <a href='/'>[Home]</a>", 201
    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')

    if not user_id:
        return "User ID is required. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user exists before deletion
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if not existing_user:
            return "User not found. <a href='/'>[Home]</a>", 404

        # Add entry to users_logs table BEFORE deleting the user
        cursor.execute(
            "INSERT INTO users_logs (user_id, event_type) VALUES (%s, 'DELETED')",
            (user_id,)
        )
        
        cursor.execute("""
            UPDATE sessions
               SET logout_time = NOW()
             WHERE user_id = %s
               AND logout_time IS NULL
        """, (user_id,))

        # Delete the user from the database
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()

        return f"User {user_id} deleted successfully. <a href='/'>[Home]</a>", 200
    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/products')
def products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.name, p.category, 
               CASE WHEN COUNT(r.review_id) = 0 THEN NULL ELSE AVG(r.rating) END AS avg_rating
        FROM products p
        LEFT JOIN reviews r ON p.id = r.product_id
        GROUP BY p.id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # rows는 DB 조회 결과 (list[dict]) 형태

    # 1) HTML을 렌더링하는 콜백 함수 정의
    def render_products_html(data):
        if not data:
            return "No products found. <a href='/'>[Home]</a>"

        html = "<h1>Product List</h1><ul>"
        for row in data:
            avg_rating = "None" if row['avg_rating'] is None else f"{row['avg_rating']:.1f}"
            html += (f"<li><a href='/product?id={row['id']}'>{row['name']} ({row['category']}) - "
                     f"Average Rating: {avg_rating}</a></li>")
        html += "</ul><a href='/'>[Home]</a>"
        return html

    return respond_html_or_json(rows, render_products_html)

@app.route('/product')
def product_detail():
    product_id = request.args.get('id')
    user_id = request.cookies.get('user_id')  # 현재 로그인된 사용자 확인
    session_id = get_or_create_session_id()  # 세션 ID 가져오기

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 상품 정보 가져오기
    cursor.execute("""
        SELECT p.id, p.name, p.price, p.category, 
               CASE WHEN COUNT(r.review_id) = 0 THEN NULL ELSE AVG(r.rating) END AS avg_rating
        FROM products p
        LEFT JOIN reviews r ON p.id = r.product_id
        WHERE p.id = %s
        GROUP BY p.id
    """, (product_id,))
    product = cursor.fetchone()

    # 리뷰 목록 가져오기
    cursor.execute("""
        SELECT r.rating, r.review_time, u.name AS reviewer_name
        FROM reviews r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.product_id = %s
        ORDER BY r.review_time DESC
    """, (product_id,))
    reviews = cursor.fetchall()

    # 장바구니 내 기존 수량 확인
    cursor.execute("""
        SELECT quantity
        FROM cart
        WHERE session_id = %s AND product_id = %s
    """, (session_id, product_id))
    cart_item = cursor.fetchone()

    cursor.close()
    conn.close()

    if product:
        # JSON 응답을 위한 데이터 구성
        data_for_json = {
            "product": {
                "id": product['id'],
                "name": product['name'],
                "price": str(product['price']),  # Decimal을 문자열로 변환
                "category": product['category'],
                "avg_rating": product['avg_rating'] if product['avg_rating'] is not None else None
            },
            "reviews": [
                {
                    "rating": review['rating'],
                    "review_time": review['review_time'].isoformat(),
                    "reviewer_name": review['reviewer_name']
                } for review in reviews
            ],
            "cart_quantity": cart_item['quantity'] if cart_item else 0
        }

        # HTML 렌더링을 위한 콜백 함수 정의
        def render_product_html(data):
            product = data['product']
            reviews = data['reviews']
            cart_quantity = data['cart_quantity']

            html = f"""
            <h1>Product Detail</h1>
            <ul>
                <li>ID: {product['id']}</li>
                <li>Name: {product['name']}</li>
                <li>Price: {product['price']}</li>
                <li>Category: {product['category']}</li>
                <li>Average Rating: {"None" if product['avg_rating'] is None else f"{product['avg_rating']:.1f}"}</li>
                <li>Reviews:
                    <ul>
            """
            if reviews:
                for i, review in enumerate(reviews):
                    if i < 5:
                        html += (f"<li>Rating: {review['rating']}, Reviewed by: {review['reviewer_name']}, "
                                 f"Time: {review['review_time']}</li>")
                    else:
                        html += "<li>...</li>"
                        break
            else:
                html += "<li>None</li>"

            html += "</ul></li></ul>"

            # 장바구니 추가/수정 기능 (사용자가 로그인한 경우)
            if user_id:
                html += f"""
                <form action="/cart/add" method="post">
                    <input type="hidden" name="id" value="{product['id']}">
                    <label for="quantity">Quantity (Current: {cart_quantity}):</label>
                    <input type="number" id="quantity" name="quantity" min="1" value="1" required>
                    <button type="submit">Add to Cart</button>
                </form>
                """

            html += "<a href='/'>[Home]</a>"
            return html

        return respond_html_or_json(data_for_json, render_product_html)

    return "Product not found. <a href='/'>[Home]</a>", 404




@app.route('/login', methods=['POST'])
def login():
    user_id = request.form.get('user_id')
    existing_user_id = request.cookies.get('user_id')
    existing_session_id = request.cookies.get('session_id')

    if not user_id:
        return "User ID is required. <a href='/'>[Home]</a>", 400

    if existing_user_id == user_id:
        return f"Already logged in as {user_id}. <a href='/'>[Home]</a>", 200

    # 기존 user_id와 다른 ID로 로그인하려는 경우 새로운 세션 ID 생성
    if existing_user_id and existing_user_id != user_id:
        #기존 세션에 로그아웃 처리
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions
                   SET logout_time = NOW()
                 WHERE session_id = %s
            """, (existing_session_id,))
            conn.commit()
        except Exception as e:
            print(f"Failed to logout old session: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        # 새로운 세션 생성
        session_id = create_session_id()
    else:
        session_id = get_or_create_session_id()

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 사용자 인증
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return "User not found. <a href='/'>[Home]</a>", 404
        
        # 세션 테이블의 user_id 필드 업데이트
        cursor.execute("""
            UPDATE sessions
               SET user_id = %s,
                   login_time = NOW()
             WHERE session_id = %s
        """, (user_id, session_id))
        conn.commit()

        cursor.close()
        conn.close()

        # 응답 생성
        resp = make_response(f"""
        <h1>Logged In</h1>
        <ul>
            <li>User ID: {user['user_id']}</li>
            <li>Name: {user['name']}</li>
            <li>Email: {user['email']}</li>
            <li>Gender: {user['gender']}</li>
            <li>Age: {user['age']}</li>
        </ul><a href='/'>[Home]</a>
        """)
        resp.set_cookie('user_id', user_id)
        resp.set_cookie('session_id', session_id)
            
        return resp
    except mysql.connector.Error as e:
        return f"Database Error {e.errno}: {e.msg}. <a href='/'>[Home]</a>", 500
    except Exception as e:
        return f"An unexpected error occurred: {e}. <a href='/'>[Home]</a>", 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()



@app.route('/categories')
def categories():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT category FROM products")
        rows = cursor.fetchall()

        # 데이터 구성: JSON 응답을 위한 데이터
        data_for_json = {
            "categories": [row['category'] for row in rows]
        }

        # HTML 렌더링을 위한 콜백 함수 정의
        def render_categories_html(data):
            categories = data['categories']
            if categories:
                html = "<h1>Categories</h1><ul>"
                for category in categories:
                    html += f"<li><a href='/category?name={category}'>{category}</a></li>"
                html += "</ul><a href='/'>[Home]</a>"
                return html
            else:
                return "No categories found. <a href='/'>[Home]</a>"

        # respond_html_or_json 함수를 호출하여 적절한 응답 반환
        return respond_html_or_json(data_for_json, render_categories_html)

    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            

@app.route('/category')
def category():
    category_name = request.args.get('name')
    if not category_name:
        return "Category name is required. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM products WHERE category = %s", (category_name,))
        rows = cursor.fetchall()

        # 데이터 구성: JSON 응답을 위한 데이터
        data_for_json = {
            "category": category_name,
            "products": [
                {
                    "id": row['id'],
                    "name": row['name']
                } for row in rows
            ]
        }

        # HTML 렌더링을 위한 콜백 함수 정의
        def render_category_html(data):
            category = data['category']
            products = data['products']

            if products:
                html = f"<h1>Products in {category}</h1><ul>"
                for product in products:
                    html += f"<li><a href='/product?id={product['id']}'>{product['id']} - {product['name']}</a></li>"
                html += "</ul><a href='/'>[Home]</a>"
                return html
            else:
                return f"No products found in {category} category. <a href='/'>[Home]</a>"

        # respond_html_or_json 함수를 호출하여 적절한 응답 반환
        return respond_html_or_json(data_for_json, render_category_html)

    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
            

@app.route('/logout', methods=['POST'])
def logout():
    session_id = request.cookies.get('session_id')
    
    if session_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE sessions
                SET logout_time = NOW()
                WHERE session_id = %s
            """, (session_id,))

            conn.commit()
        except Exception as e:
            print(f"Error in logout: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    resp = make_response("Logged Out. <a href='/'>[Home]</a>")
    resp.delete_cookie('session_id')
    resp.delete_cookie('user_id')
    return resp



@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    session_id = get_or_create_session_id()  # Retrieve session ID from cookies

    if not query:
        return "Search query is required. <a href='/'>[Home]</a>", 400

    if not session_id:
        return "Session ID is required. Please visit the homepage to create a session. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if session_id exists in the sessions table
        cursor.execute("SELECT session_id FROM sessions WHERE session_id = %s", (session_id,))
        session_exists = cursor.fetchone()

        if not session_exists:
            return "Invalid session. Please visit the homepage to create a session. <a href='/'>[Home]</a>", 400

        # Perform the search
        cursor.execute("SELECT id, name FROM products WHERE name LIKE %s OR category LIKE %s", (f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()

        # Log the search query
        cursor.execute(
            "INSERT INTO search_logs (session_id, search_query, searched_at) VALUES (%s, %s, NOW())",
            (session_id, query)
        )
        conn.commit()

        # 데이터 구성: JSON 응답을 위한 데이터
        data_for_json = {
            "query": query,
            "results": [
                {
                    "id": row['id'],
                    "name": row['name']
                } for row in rows
            ]
        }

        # HTML 렌더링을 위한 콜백 함수 정의
        def render_search_html(data):
            query = data['query']
            results = data['results']

            if results:
                html = f"<h1>Search Results for '{query}'</h1><ul>"
                for item in results:
                    html += f"<li><a href='/product?id={item['id']}'>{item['name']}</a></li>"
                html += "</ul><a href='/'>[Home]</a>"
                return html
            else:
                return f"No results found for '{query}'. <a href='/'>[Home]</a>"

        # respond_html_or_json 함수를 호출하여 적절한 응답 반환
        return respond_html_or_json(data_for_json, render_search_html)

    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('id')
    user_id = request.cookies.get('user_id')  # 사용자 ID 가져오기
    session_id = get_or_create_session_id()  # 세션 ID 가져오기
    quantity = request.form.get('quantity', 1)  # 기본 수량은 1

    if not product_id or not user_id or not session_id:
        return "Product ID, User ID, and Session ID are required. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if the product exists and fetch its price
        cursor.execute("SELECT id, price FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            cursor.close()
            conn.close()
            return "Invalid product. <a href='/'>[Home]</a>", 404

        product_price = product['price']

        # Check if the product is already in the cart for this session
        cursor.execute(
            "SELECT cart_id, quantity FROM cart WHERE session_id = %s AND product_id = %s",
            (session_id, product_id)
        )
        cart_item = cursor.fetchone()

        if cart_item:
            old_quantity = cart_item['quantity']
            new_quantity = old_quantity + int(quantity)
            cursor.execute(
                "UPDATE cart SET quantity = %s WHERE session_id = %s AND product_id = %s",
                (new_quantity, session_id, product_id)
            )

            cursor.execute(
                """
                INSERT INTO cart_logs (
                    cart_id, session_id, user_id, product_id,
                    old_quantity, new_quantity, price, event_type, event_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'UPDATED', NOW())
                """,
                (cart_item['cart_id'], session_id, user_id, product_id,
                 old_quantity, new_quantity, product_price)
            )
        else:
            # Insert new item into the cart
            cursor.execute(
                "INSERT INTO cart (session_id, user_id, product_id, quantity, price, added_at) VALUES (%s, %s, %s, %s, %s, NOW())",
                (session_id, user_id, product_id, quantity, product_price)
            )

            # Get the cart_id of the newly inserted item
            cursor.execute(
                "SELECT cart_id FROM cart WHERE session_id = %s AND product_id = %s",
                (session_id, product_id)
            )
            new_cart_id = cursor.fetchone()['cart_id']

            # cart_logs 테이블에 ADDED 기록
            cursor.execute(
                """
                INSERT INTO cart_logs (
                    cart_id, session_id, user_id, product_id,
                    old_quantity, new_quantity, price, event_type, event_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'ADDED', NOW())
                """,
                (new_cart_id, session_id, user_id, product_id,
                 0, int(quantity), product_price)
            )

        conn.commit()
        cursor.close()
        conn.close()

        return f"Product {product_id} added to cart. Quantity: {quantity}. <a href='/'>[Home]</a>"
    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500



@app.route('/cart/view', methods=['GET'])
def view_cart():
    user_id = request.cookies.get('user_id')  # 사용자 ID 가져오기
    session_id = get_or_create_session_id()  # 세션 ID 가져오기

    if not user_id or not session_id:
        return "User ID and Session ID are required. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 현재 세션의 장바구니 아이템 가져오기
        cursor.execute("""
            SELECT c.product_id, p.name, c.price, c.quantity, (c.price * c.quantity) AS total_price
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.session_id = %s
        """, (session_id,))
        cart_items = cursor.fetchall()

        # 데이터 구성: JSON 응답을 위한 데이터
        data_for_json = {
            "user_id": user_id,
            "session_id": session_id,
            "cart_items": [
                {
                    "product_id": item['product_id'],
                    "name": item['name'],
                    "price": str(item['price']),         # Decimal을 문자열로 변환
                    "quantity": item['quantity'],
                    "total_price": str(item['total_price'])  # Decimal을 문자열로 변환
                } for item in cart_items
            ],
            "total_cost": str(sum(float(item['total_price']) for item in cart_items))
        }

        # HTML 렌더링을 위한 콜백 함수 정의
        def render_view_cart_html(data):
            cart_items = data['cart_items']
            total_cost = data['total_cost']

            if cart_items:
                html = "<h1>Your Cart</h1><ul>"
                for item in cart_items:
                    html += f"""
                        <li>
                            Product: {item['name']} - Price: {item['price']} - Quantity: {item['quantity']} - Total: {item['total_price']}
                        </li>
                    """
                html += f"</ul><p>Total Cost: {total_cost}</p><a href='/'>[Home]</a>"
                return html
            else:
                return "Your cart is empty. <a href='/'>[Home]</a>"

        # respond_html_or_json 함수를 호출하여 적절한 응답 반환
        return respond_html_or_json(data_for_json, render_view_cart_html)

    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')  # 삭제할 상품 ID
    quantity_to_remove = int(request.form.get('quantity', 0))  # 삭제할 수량
    session_id = get_or_create_session_id()  # 세션 ID 가져오기

    if not session_id:
        return "Session ID is required. <a href='/'>[Home]</a>", 400

    if not product_id or quantity_to_remove <= 0:
        return "Product ID and a valid quantity are required to remove items from the cart. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if the product exists in the cart
        cursor.execute(
            "SELECT cart_id, quantity, price FROM cart WHERE session_id = %s AND product_id = %s",
            (session_id, product_id)
        )
        cart_item = cursor.fetchone()

        if not cart_item:
            return f"No product with ID {product_id} found in the cart. <a href='/'>[Home]</a>", 404

        current_quantity = cart_item['quantity']
        cart_id = cart_item['cart_id']
        product_price = cart_item['price']

        if quantity_to_remove > current_quantity:
            # If trying to remove more than available quantity
            return f"Cannot remove {quantity_to_remove} items. Only {current_quantity} items available in the cart. <a href='/'>[Home]</a>", 400

        if quantity_to_remove == current_quantity:
            # If removing equal to current quantity, delete the item
            cursor.execute(
                "DELETE FROM cart WHERE session_id = %s AND product_id = %s",
                (session_id, product_id)
            )
            action = 'REMOVED'
            old_quantity = current_quantity
            new_quantity = 0
            message = f"Product {product_id} completely removed from the cart."
        else:
            # Otherwise, reduce the quantity
            new_quantity = current_quantity - quantity_to_remove
            cursor.execute(
                "UPDATE cart SET quantity = %s WHERE session_id = %s AND product_id = %s",
                (new_quantity, session_id, product_id)
            )
            action = 'UPDATED'
            old_quantity = current_quantity
            message = f"Product {product_id} quantity reduced to {new_quantity} in the cart."

        # Log the action to cart_logs
        cursor.execute(
            """
            INSERT INTO cart_logs (
                cart_id, session_id, user_id, product_id,
                old_quantity, new_quantity, price, event_type, event_time
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (cart_id, session_id, request.cookies.get('user_id'), product_id,
             old_quantity, new_quantity, product_price, action)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return f"{message} <a href='/'>[Home]</a>"
    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500



@app.route('/checkout', methods=['POST'])
def checkout():
    user_id = request.cookies.get('user_id')
    session_id = get_or_create_session_id()  # 세션 ID 가져오기

    if not user_id or not session_id:
        return "User ID and Session ID are required. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all cart items for the current session
        cursor.execute("""
            SELECT c.cart_id, c.product_id, c.price, c.quantity, p.name
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.session_id = %s
        """, (session_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            return "Your cart is empty. <a href='/'>[Home]</a>"

        # Process each cart item as an order
        for item in cart_items:
            order_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO orders (order_id, user_id, session_id, product_id, price, quantity, order_time)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (order_id, user_id, session_id, item['product_id'], item['price'], item['quantity'])
            )

            # cart_logs: CHECKED_OUT
            old_quantity = item['quantity']
            new_quantity = 0
            cursor.execute("""
                INSERT INTO cart_logs (
                    cart_id, session_id, user_id, product_id,
                    old_quantity, new_quantity, price, event_type, event_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'CHECKED_OUT', NOW())
            """, (
                item['cart_id'], session_id, user_id, item['product_id'],
                old_quantity, new_quantity, item['price']
            ))

        # Clear the cart after checkout
        cursor.execute("DELETE FROM cart WHERE session_id = %s", (session_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return "Checkout successful. Your cart is now empty. <a href='/'>[Home]</a>"
    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500




@app.route('/checkout_history')
def checkout_history():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return "User ID is required to view checkout history. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 주문 목록 가져오기
        cursor.execute("""
            SELECT o.order_id, p.name AS product_name, o.price, o.quantity, 
                   (o.price * o.quantity) AS total_price, o.order_time
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.user_id = %s
            ORDER BY o.order_time DESC
        """, (user_id,))
        orders = cursor.fetchall()

        # 데이터 구성: JSON 응답을 위한 데이터
        data_for_json = {
            "user_id": user_id,
            "checkout_history": [
                {
                    "order_id": order['order_id'],
                    "product_name": order['product_name'],
                    "price": str(order['price']),  # Decimal을 문자열로 변환
                    "quantity": order['quantity'],
                    "total_price": str(order['total_price']),  # Decimal을 문자열로 변환
                    "order_time": order['order_time'].isoformat()
                } for order in orders
            ]
        }

        # HTML 렌더링을 위한 콜백 함수 정의
        def render_checkout_history_html(data):
            user_id = data['user_id']
            checkout_history = data['checkout_history']

            if checkout_history:
                html = f"<h1>Checkout History for User: {user_id}</h1><ul>"
                for order in checkout_history:
                    html += (f"<li>Order ID: {order['order_id']}, Product: {order['product_name']}, "
                             f"Price: {order['price']} x {order['quantity']} = {order['total_price']}, "
                             f"Time: {order['order_time']}</li>")
                html += "</ul><a href='/'>[Home]</a>"
                return html
            else:
                return f"No checkout history found for User ID: {user_id}. <a href='/'>[Home]</a>"

        # respond_html_or_json 함수를 호출하여 적절한 응답 반환
        return respond_html_or_json(data_for_json, render_checkout_history_html)

    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/add_review', methods=['POST'])
def add_review():
    product_id = request.form.get('product_id')
    rating = request.form.get('rating')
    user_id = request.cookies.get('user_id')
    session_id = get_or_create_session_id()  # 세션 ID 추가

    if not product_id or not rating or not user_id or not session_id:
        return "Product ID, Rating, User ID, and Session ID are required. <a href='/'>[Home]</a>", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if the product exists
        cursor.execute("SELECT id FROM products WHERE id = %s", (product_id,))
        product_exists = cursor.fetchone()
        if not product_exists:
            return "Invalid Product ID. <a href='/'>[Home]</a>", 404

        # Check if the session exists
        cursor.execute("SELECT session_id FROM sessions WHERE session_id = %s", (session_id,))
        session_exists = cursor.fetchone()
        if not session_exists:
            return "Invalid Session ID. <a href='/'>[Home]</a>", 404

        # Check if the user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        user_exists = cursor.fetchone()
        if not user_exists:
            return "Invalid User ID. <a href='/'>[Home]</a>", 404

        # Add review
        review_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO reviews (review_id, product_id, rating, user_id, session_id, review_time) VALUES (%s, %s, %s, %s, %s, NOW())",
            (review_id, product_id, rating, user_id, session_id)
        )
        conn.commit()
        return f"Review added for Product {product_id} with rating {rating} by User {user_id}, Session ID: {session_id}. <a href='/'>[Home]</a>"
    except Exception as e:
        return f"An error occurred: {e}. <a href='/'>[Home]</a>", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/error')
def error():
    return 1/0
    

    
            
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOL

log "Flask application setup completed successfully."

# 4. 워커 및 스레드 개수 계산
log "Calculating Gunicorn workers and threads..."
CPU_CORES=$(nproc)
WORKERS=$((CPU_CORES * 2 + 1))  # 공식: (코어 수 * 2) + 1
THREADS=4                       # 스레드 기본값 (I/O 바운드 환경)
log "Detected $CPU_CORES CPU cores: setting $WORKERS workers and $THREADS threads."

# 5. Gunicorn 서비스 파일 생성
log "Creating Gunicorn service..."

# 이하 Gunicorn, Nginx 설정 부분은 동일
LOG_FORMAT_NAME="custom_json"

cat > /etc/systemd/system/flask_app.service <<EOL
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/gunicorn --workers $WORKERS --threads $THREADS -b 127.0.0.1:8080 app:app

[Install]
WantedBy=multi-user.target
EOL

run_command systemctl daemon-reload
run_command systemctl enable flask_app
run_command systemctl start flask_app

NGINX_CONF_MAIN="/etc/nginx/nginx.conf"

if ! grep -q "log_format $LOG_FORMAT_NAME" $NGINX_CONF_MAIN; then
    echo "Adding custom_json log format to NGINX configuration..."
    sed -i "/http {/a \
        log_format $LOG_FORMAT_NAME escape=json '{\\n\
            \"timestamp\":\"\$time_local\",\\n\
            \"remote_addr\":\"\$remote_addr\",\\n\
            \"request\":\"\$request\",\\n\
            \"status\":\"\$status\",\\n\
            \"body_bytes_sent\":\"\$body_bytes_sent\",\\n\
            \"http_referer\":\"\$http_referer\",\\n\
            \"http_user_agent\":\"\$http_user_agent\",\\n\
            \"session_id\":\"\$cookie_session_id\",\\n\
            \"user_id\":\"\$cookie_user_id\",\\n\
            \"request_time\":\"\$request_time\",\\n\
            \"upstream_response_time\":\"\$upstream_response_time\",\\n\
            \"endpoint\":\"\$uri\",\\n\
            \"method\":\"\$request_method\",\\n\
            \"query_params\":\"\$args\",\\n\
            \"product_id\":\"\$arg_id\",\\n\
            \"category\":\"\$arg_name\",\\n\
            \"x_forwarded_for\":\"\$http_x_forwarded_for\",\\n\
            \"host\":\"\$host\"\\n\
        }';" $NGINX_CONF_MAIN
    echo "custom_json log format added successfully."
else
    echo "custom_json log format already exists. Skipping addition."
fi


NGINX_CONF="/etc/nginx/sites-available/flask_app"
cat > $NGINX_CONF <<EOL
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    error_log /var/log/nginx/flask_app_error.log;
    access_log /var/log/nginx/flask_app_access.log $LOG_FORMAT_NAME;
}
EOL

run_command ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
run_command rm -f /etc/nginx/sites-enabled/default

run_command nginx -t
run_command systemctl restart nginx

log "Setup complete. Flask application is running with Gunicorn and Nginx."
echo "You can access your application at http://<your_server_ip>/"
