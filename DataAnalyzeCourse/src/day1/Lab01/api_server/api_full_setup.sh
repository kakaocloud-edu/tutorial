#!/bin/bash

echo "MYSQL_HOST set to: $MYSQL_HOST"
source /home/ubuntu/.bashrc

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
from flask import Flask, request, make_response, jsonify, g
import uuid
import time
import random
import mysql.connector
import json
import logging
from datetime import datetime
from mysql.connector import Error
from flask.json import JSONEncoder
from decimal import Decimal

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(CustomJSONEncoder, self).default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

DB_CONFIG = {
    'user': 'admin',
    'password': 'admin1234',
    'host': 'az-a.database-lsh.ae90ddc1b6dc4b0581bb44b31f8921b5.mysql.managed-service.kr-central-2.kakaocloud.com',
    'database': 'shopdb',
    'ssl_disabled': True
}

# =====================================
# 헬퍼 함수들 (강화된 버전)
# =====================================

def get_request_data(key, default=None):
    """JSON과 form 데이터를 모두 지원하는 헬퍼 함수"""
    try:
        if request.is_json and request.get_json():
            return request.get_json().get(key, default)
        return request.form.get(key, default)
    except Exception as e:
        logger.error(f"get_request_data 오류: {e}")
        return default

def get_db_connection():
    """DB 연결을 안전하게 생성"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        logger.error(f"DB 연결 실패: {e}")
        raise

def respond_html_or_json(data, html_renderer):
    """HTML 또는 JSON 응답 자동 선택"""
    try:
        accept_header = request.headers.get("Accept", "")
        if "application/json" in accept_header:
            return jsonify(data)
        else:
            return html_renderer(data)
    except Exception as e:
        logger.error(f"응답 생성 오류: {e}")
        return jsonify({"error": "응답 생성 실패"}), 500

def safe_get_or_create_session_id():
    """관대한 세션 ID 생성 (검증 없음)"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT IGNORE INTO sessions (session_id, created_at) VALUES (%s, NOW())",
                (session_id,)
            )
            conn.commit()
        except Exception as e:
            logger.warning(f"세션 생성 실패 (무시): {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
    return session_id

def safe_ensure_user_exists(user_id):
    """사용자 존재 보장 (없으면 즉시 생성)"""
    if not user_id:
        return None
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 사용자 존재 확인
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if cursor.fetchone():
            return user_id
        
        # 없으면 기본 정보로 생성 (IGNORE로 중복 에러 방지)
        cursor.execute("""
            INSERT IGNORE INTO users (user_id, name, email, gender, age) 
            VALUES (%s, %s, %s, 'M', 25)
        """, (user_id, f"Auto {user_id}", f"{user_id}@auto.com"))
        
        cursor.execute("""
            INSERT IGNORE INTO users_logs (user_id, event_type) 
            VALUES (%s, 'AUTO_CREATED')
        """, (user_id,))
        
        conn.commit()
        logger.info(f"사용자 자동 생성: {user_id}")
        return user_id
        
    except Exception as e:
        logger.error(f"사용자 생성/확인 실패: {e}")
        return user_id  # 실패해도 일단 반환
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

# =====================================
# 에러 핸들러
# =====================================

@app.errorhandler(400)
def handle_400(e):
    return jsonify({"error": "잘못된 요청"}), 400

@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "리소스를 찾을 수 없음"}), 404

@app.errorhandler(500)
def handle_500(e):
    logger.error(f"내부 서버 오류: {e}")
    return jsonify({"error": "내부 서버 오류"}), 500

# =====================================
# 미들웨어 (관대한 버전)
# =====================================

@app.before_request
def safe_update_last_active():
    """세션 활동 시간 업데이트 (실패해도 계속 진행)"""
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
            logger.warning(f"last_active 업데이트 실패 (무시): {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()

# =====================================
# 사용자 존재 확인 엔드포인트
# =====================================

@app.route('/users/<user_id>/exists', methods=['GET'])
def check_user_exists(user_id):
    """사용자 존재 여부 확인 (관대한 처리)"""
    if not user_id or user_id.strip() == '':
        return jsonify({"error": "user_id가 필요함"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            return jsonify({"exists": True, "user_id": user_id}), 200
        else:
            return jsonify({"exists": False, "user_id": user_id}), 404
            
    except Exception as e:
        logger.error(f"사용자 존재 확인 오류: {e}")
        # 에러 시에도 존재한다고 응답 (관대한 처리)
        return jsonify({"exists": True, "user_id": user_id}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

# =====================================
# 메인 라우트
# =====================================

@app.route('/')
def home():
    html = """
    <h1>Online Shopping Mall</h1>
    <p>이 사이트는 쇼핑몰 데이터를 축적하기 위한 테스트 환경임.</p>
    <ul>
        <li><a href="/products">Products</a></li>
        <li><a href="/search?q=test">Search</a></li>
        <li><a href="/cart/view">Cart</a></li>
        <li><a href="/categories">Categories</a></li>
    </ul>
    """
    
    try:
        resp = make_response(html)
        session_id = safe_get_or_create_session_id()
        resp.set_cookie('session_id', session_id)
        return resp
    except Exception as e:
        logger.error(f"홈페이지 로딩 오류: {e}")
        return "Homepage", 200

# =====================================
# 검색 엔드포인트 (완전 수정)
# =====================================

@app.route('/search')
def search():
    """검색 기능 - 관대한 검증"""
    try:
        # 1. 파라미터 우선 검증 (세션 검증보다 먼저)
        query = request.args.get('q') or request.args.get('query', '').strip()
        if not query:
            return jsonify({
                "error": "Search query required", 
                "message": "Use 'q' or 'query' parameter"
            }), 400

        # 2. 세션 생성 (검증 안 함, 실패해도 진행)
        session_id = safe_get_or_create_session_id()
        
        # 3. 상품 검색 수행
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, category FROM products 
            WHERE name LIKE %s OR category LIKE %s
            LIMIT 20
        """, (f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        
        # 4. 검색 로그 저장 (실패해도 검색 결과는 반환)
        try:
            cursor.execute("""
                INSERT IGNORE INTO search_logs (session_id, search_query, searched_at) 
                VALUES (%s, %s, NOW())
            """, (session_id, query))
            conn.commit()
        except Exception as log_error:
            logger.warning(f"검색 로그 저장 실패 (무시): {log_error}")
        
        # 5. 성공 응답
        data_for_json = {
            "query": query,
            "session_id": session_id,
            "results": [
                {
                    "id": row['id'],
                    "name": row['name'],
                    "category": row['category']
                } for row in rows
            ]
        }

        def render_search_html(data):
            query = data['query']
            results = data['results']
            
            if results:
                html = f"<h1>Search Results for '{query}'</h1><ul>"
                for item in results:
                    html += f"<li><a href='/product?id={item['id']}'>{item['name']} ({item['category']})</a></li>"
                html += "</ul><a href='/'>[Home]</a>"
                return html
            else:
                return f"No results found for '{query}'. <a href='/'>[Home]</a>"

        return respond_html_or_json(data_for_json, render_search_html)
        
    except mysql.connector.Error as e:
        logger.error(f"DB 오류 - search: {e}")
        # DB 오류 시에도 빈 결과 반환 (서비스 중단 방지)
        return jsonify({
            "query": query if 'query' in locals() else "unknown",
            "results": [],
            "message": "Search temporarily unavailable"
        }), 200
    except Exception as e:
        logger.error(f"검색 오류: {e}")
        return jsonify({
            "query": query if 'query' in locals() else "unknown", 
            "results": [],
            "error": "Search failed"
        }), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

# =====================================
# 장바구니 관리 (완전 수정)
# =====================================

@app.route('/cart/add', methods=['GET', 'POST'])
def add_to_cart():
    """장바구니 추가 - 관대한 사용자/세션 처리"""
    try:
        # 1. 파라미터 추출
        product_id = request.args.get('id') or get_request_data('product_id')
        quantity = int(request.args.get('quantity', 1))
        
        if not product_id:
            return jsonify({"error": "Product ID required"}), 400
            
        # 2. 세션 및 사용자 정보 확보
        session_id = safe_get_or_create_session_id()
        user_id = request.cookies.get('user_id')
        
        # 사용자가 없으면 게스트 사용자 생성
        if not user_id:
            user_id = f"guest_{session_id[:8]}"
        
        # 사용자 존재 보장 (없으면 자동 생성)
        user_id = safe_ensure_user_exists(user_id)
        
        # 3. DB 연결 및 상품 확인
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, price FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({"error": "Product not found"}), 404
            
        # 4. 안전한 장바구니 추가 (중복 키 에러 방지)
        try:
            # 먼저 기존 항목 확인
            cursor.execute("""
                SELECT cart_id, quantity FROM cart 
                WHERE session_id = %s AND product_id = %s
            """, (session_id, product_id))
            existing_cart = cursor.fetchone()
            
            if existing_cart:
                # 기존 항목 업데이트
                new_quantity = existing_cart['quantity'] + quantity
                cursor.execute("""
                    UPDATE cart SET quantity = %s, price = %s 
                    WHERE cart_id = %s
                """, (new_quantity, product['price'], existing_cart['cart_id']))
            else:
                # 새 항목 추가
                cursor.execute("""
                    INSERT INTO cart (session_id, user_id, product_id, quantity, price, added_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (session_id, user_id, product_id, quantity, product['price']))
            
            conn.commit()
            
            # 5. 성공 응답
            resp = make_response(jsonify({
                "success": True,
                "message": f"Product {product_id} added to cart",
                "user_id": user_id,
                "session_id": session_id,
                "quantity": quantity
            }))
            
            # 쿠키 설정
            resp.set_cookie('user_id', user_id, max_age=86400*30)
            resp.set_cookie('session_id', session_id, max_age=86400)
            
            return resp, 200
            
        except mysql.connector.Error as e:
            logger.error(f"장바구니 DB 오류: {e}")
            # DB 오류 시에도 성공으로 응답 (서비스 중단 방지)
            return jsonify({
                "success": False,
                "message": "Cart service temporarily unavailable",
                "user_id": user_id,
                "session_id": session_id
            }), 200
        
    except Exception as e:
        logger.error(f"장바구니 추가 오류: {e}")
        # 모든 오류를 200으로 처리하여 서비스 중단 방지
        return jsonify({
            "success": False,
            "message": "Cart add failed but service continues",
            "error": str(e)
        }), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

# =====================================
# 기타 필수 엔드포인트들
# =====================================

@app.route('/products')
def products():
    """상품 목록"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, category FROM products LIMIT 50")
        rows = cursor.fetchall()
        
        def render_products_html(data):
            if not data:
                return "No products found. <a href='/'>[Home]</a>"
            html = "<h1>Product List</h1><ul>"
            for row in data:
                html += f"<li><a href='/product?id={row['id']}'>{row['name']} ({row['category']})</a></li>"
            html += "</ul><a href='/'>[Home]</a>"
            return html

        return respond_html_or_json(rows, render_products_html)
        
    except Exception as e:
        logger.error(f"상품 목록 오류: {e}")
        return jsonify({"products": [], "message": "Products temporarily unavailable"}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/product')
def product_detail():
    """상품 상세"""
    try:
        product_id = request.args.get('id')
        if not product_id:
            return jsonify({"error": "Product ID required"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, price, category FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify({
            "product": {
                "id": product['id'],
                "name": product['name'],
                "price": str(product['price']),
                "category": product['category']
            }
        })
        
    except Exception as e:
        logger.error(f"상품 상세 오류: {e}")
        return jsonify({"error": "Product detail unavailable"}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/categories')
def categories():
    """카테고리 목록"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT category FROM products")
        rows = cursor.fetchall()
        
        categories = [row['category'] for row in rows]
        
        def render_categories_html(data):
            if data:
                html = "<h1>Categories</h1><ul>"
                for category in data:
                    html += f"<li><a href='/category?category={category}'>{category}</a></li>"
                html += "</ul><a href='/'>[Home]</a>"
                return html
            return "No categories found. <a href='/'>[Home]</a>"

        return respond_html_or_json(categories, render_categories_html)
        
    except Exception as e:
        logger.error(f"카테고리 오류: {e}")
        return jsonify({"categories": [], "message": "Categories temporarily unavailable"}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/category')
def category():
    """카테고리별 상품"""
    try:
        category_name = request.args.get('category') or request.args.get('name')
        if not category_name:
            return jsonify({"error": "Category parameter required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM products WHERE category = %s LIMIT 20", (category_name,))
        rows = cursor.fetchall()

        data = {
            "category": category_name,
            "products": [{"id": row['id'], "name": row['name']} for row in rows]
        }

        def render_category_html(data):
            category = data['category']
            products = data['products']
            if products:
                html = f"<h1>Products in {category}</h1><ul>"
                for product in products:
                    html += f"<li><a href='/product?id={product['id']}'>{product['name']}</a></li>"
                html += "</ul><a href='/'>[Home]</a>"
                return html
            return f"No products in {category}. <a href='/'>[Home]</a>"

        return respond_html_or_json(data, render_category_html)
        
    except Exception as e:
        logger.error(f"카테고리별 상품 오류: {e}")
        return jsonify({"category": category_name if 'category_name' in locals() else "unknown", "products": []}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/cart/view')
def view_cart():
    """장바구니 조회"""
    try:
        session_id = safe_get_or_create_session_id()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.product_id, p.name, c.price, c.quantity, (c.price * c.quantity) AS total_price
            FROM cart c
            LEFT JOIN products p ON c.product_id = p.id
            WHERE c.session_id = %s
        """, (session_id,))
        cart_items = cursor.fetchall()

        return jsonify({
            "session_id": session_id,
            "cart_items": [
                {
                    "product_id": item['product_id'],
                    "name": item['name'] or f"Product {item['product_id']}",
                    "price": str(item['price']),
                    "quantity": item['quantity'],
                    "total_price": str(item['total_price'])
                } for item in cart_items
            ],
            "total_cost": str(sum(float(item['total_price'] or 0) for item in cart_items))
        })
        
    except Exception as e:
        logger.error(f"장바구니 조회 오류: {e}")
        return jsonify({"cart_items": [], "total_cost": "0"}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

# =====================================
# 사용자 관리
# =====================================

@app.route('/add_user', methods=['POST'])
def add_user():
    """사용자 등록"""
    try:
        user_id = get_request_data('user_id')
        name = get_request_data('name')
        email = get_request_data('email')
        gender = get_request_data('gender')
        age = get_request_data('age')

        if not (user_id and name and email and gender and age):
            return jsonify({"error": "All fields required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT IGNORE INTO users (user_id, name, email, gender, age) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, name, email, gender, age))
        
        cursor.execute("""
            INSERT IGNORE INTO users_logs (user_id, event_type) 
            VALUES (%s, 'CREATED')
        """, (user_id,))
        
        conn.commit()
        
        return jsonify({"message": f"User {name} added successfully"}), 201
            
    except Exception as e:
        logger.error(f"사용자 추가 오류: {e}")
        return jsonify({"message": "User registration completed"}), 201
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    """로그인"""
    try:
        user_id = get_request_data('user_id')
        if not user_id:
            return jsonify({"error": "User ID required"}), 400

        # 사용자 존재 보장
        user_id = safe_ensure_user_exists(user_id)
        session_id = safe_get_or_create_session_id()

        resp = make_response(jsonify({
            "message": "Login successful",
            "user_id": user_id,
            "session_id": session_id
        }))
        
        resp.set_cookie('user_id', user_id)
        resp.set_cookie('session_id', session_id)
        return resp
        
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return jsonify({"message": "Login completed"}), 200

@app.route('/logout', methods=['POST'])
def logout():
    """로그아웃"""
    resp = make_response(jsonify({"message": "Logout successful"}))
    resp.delete_cookie('session_id')
    resp.delete_cookie('user_id')
    return resp



@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = get_request_data('user_id')  # 헬퍼 함수 사용

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


@app.route('/checkout', methods=['POST'])
def checkout():
    """결제"""
    try:
        session_id = safe_get_or_create_session_id()
        user_id = request.cookies.get('user_id')
        
        if not user_id:
            user_id = f"guest_{session_id[:8]}"
        
        user_id = safe_ensure_user_exists(user_id)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT c.product_id, c.price, c.quantity
            FROM cart c WHERE c.session_id = %s
        """, (session_id,))
        cart_items = cursor.fetchall()

        if cart_items:
            for item in cart_items:
                order_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT IGNORE INTO orders (order_id, user_id, session_id, product_id, price, quantity, order_time)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (order_id, user_id, session_id, item['product_id'], item['price'], item['quantity']))

            cursor.execute("DELETE FROM cart WHERE session_id = %s", (session_id,))
            conn.commit()

        resp = make_response(jsonify({
            "message": "Checkout successful",
            "user_id": user_id,
            "items_count": len(cart_items)
        }))
        
        if not request.cookies.get('user_id'):
            resp.set_cookie('user_id', user_id)
            
        return resp
        
    except Exception as e:
        logger.error(f"결제 오류: {e}")
        return jsonify({"message": "Checkout completed"}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/add_review', methods=['POST'])
def add_review():
    """리뷰 추가"""
    try:
        product_id = get_request_data('product_id')
        rating = get_request_data('rating')
        user_id = request.cookies.get('user_id')
        session_id = safe_get_or_create_session_id()

        if not (product_id and rating):
            return jsonify({"error": "Product ID and rating required"}), 400

        if not user_id:
            user_id = f"guest_{session_id[:8]}"
        
        user_id = safe_ensure_user_exists(user_id)

        conn = get_db_connection()
        cursor = conn.cursor()

        review_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT IGNORE INTO reviews (review_id, product_id, rating, user_id, session_id, review_time) 
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (review_id, product_id, rating, user_id, session_id))
        conn.commit()
        
        resp = make_response(jsonify({
            "message": f"Review added for product {product_id}",
            "user_id": user_id,
            "rating": rating
        }))
        
        if not request.cookies.get('user_id'):
            resp.set_cookie('user_id', user_id)
            
        return resp
        
    except Exception as e:
        logger.error(f"리뷰 추가 오류: {e}")
        return jsonify({"message": "Review submission completed"}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/checkout_history')
def checkout_history():
    """결제 내역"""
    try:
        user_id = request.cookies.get('user_id')
        if not user_id:
            return jsonify({"checkout_history": []}), 200

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT o.order_id, p.name AS product_name, o.price, o.quantity, o.order_time
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.id
            WHERE o.user_id = %s
            ORDER BY o.order_time DESC
            LIMIT 20
        """, (user_id,))
        orders = cursor.fetchall()

        return jsonify({
            "user_id": user_id,
            "checkout_history": [
                {
                    "order_id": order['order_id'],
                    "product_name": order['product_name'] or "Unknown Product",
                    "price": str(order['price']),
                    "quantity": order['quantity'],
                    "order_time": order['order_time'].isoformat() if order['order_time'] else None
                } for order in orders
            ]
        })
        
    except Exception as e:
        logger.error(f"결제 내역 오류: {e}")
        return jsonify({"checkout_history": []}), 200
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/error')
def error():
    return 1/0

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

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
            \"request\":\"\$request_method \$uri \$server_protocol\",\\n\
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
            \"category\":\"\$http_x_category\",\\n\
            \"x_forwarded_for\":\"\$http_x_forwarded_for\",\\n\
            \"host\":\"\$host\"\\n\
        }';" $NGINX_CONF_MAIN
    echo "custom_json log format added successfully."
else
    echo "custom_json log format already exists. Skipping addition."
fi


NGINX_CONF="/etc/nginx/sites-available/flask_app"
cat > $NGINX_CONF <<'EOL'
server {
    listen 80;
    server_name _;

    access_log off;
    error_log /var/log/nginx/flask_app_error.log;

    if ($uri = "") {
        return 403;
    }

    location = / {
        if ($args) {
            return 403;
        }
        access_log /var/log/nginx/flask_app_access.log custom_json;
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ~ ^/(push-subscription|push-messages|add_user|delete_user|login|logout|products|product|categories|category|search|cart/add|cart/remove|cart/view|checkout|checkout_history|add_review|error)$ {
        access_log /var/log/nginx/flask_app_access.log custom_json;
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        return 403;
    }

    error_log /var/log/nginx/flask_app_error.log;
    access_log /var/log/nginx/flask_app_access.log custom_json;
}
EOL

run_command ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
run_command rm -f /etc/nginx/sites-enabled/default

run_command nginx -t
run_command systemctl restart nginx

log "Setup complete. Flask application is running with Gunicorn and Nginx."
echo "You can access your application at http://<your_server_ip>/"
