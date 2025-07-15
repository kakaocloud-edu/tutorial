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
from flask import Flask, request, make_response, jsonify
import uuid
import time
import mysql.connector
import json
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# DB 설정
DB_CONFIG = {
    'user': 'admin',
    'password': 'admin1234',
    'host': '${MYSQL_HOST}',
    'database': 'shopdb',
    'ssl_disabled': True
}

# =====================================
# 핵심 헬퍼 함수들
# =====================================

def get_request_data():
    """JSON과 form 데이터를 확실하게 처리"""
    try:
        logger.info(f"Request Method: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        
        # JSON 데이터 우선 처리
        if request.is_json:
            data = request.get_json()
            if data:
                logger.info(f"JSON 데이터 파싱 성공: {data}")
                return data
        
        # form 데이터 처리
        if request.form:
            data = dict(request.form)
            logger.info(f"Form 데이터 파싱 성공: {data}")
            return data
        
        # URL args도 확인
        if request.args:
            data = dict(request.args)
            logger.info(f"Args 데이터 파싱: {data}")
            return data
        
        logger.warning("모든 데이터 파싱 실패")
        return {}
    except Exception as e:
        logger.error(f"데이터 파싱 에러: {e}")
        return {}

def get_db_connection():
    """DB 연결"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"DB 연결 실패: {e}")
        raise

def safe_execute(query, params=None, fetch=False):
    """안전한 DB 실행"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info(f"실행할 쿼리: {query}")
        logger.info(f"파라미터: {params}")
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            logger.info(f"조회 결과: {len(result) if result else 0}개 행")
        else:
            result = cursor.rowcount
            logger.info(f"영향받은 행: {result}개")
        
        conn.commit()
        return result
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"DB 실행 에러: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_session():
    """세션 생성"""
    session_id = str(uuid.uuid4())
    try:
        safe_execute("""
            INSERT INTO sessions (session_id, created_at) 
            VALUES (%s, NOW())
        """, (session_id,))
        logger.info(f"세션 생성 완료: {session_id}")
        return session_id
    except Exception as e:
        logger.error(f"세션 생성 실패: {e}")
        return session_id

def ensure_user_exists(user_id):
    """사용자 존재 확인 및 생성"""
    if not user_id:
        return None
    
    try:
        result = safe_execute("""
            SELECT user_id FROM users WHERE user_id = %s
        """, (user_id,), fetch=True)
        
        if result:
            return user_id
        
        safe_execute("""
            INSERT IGNORE INTO users (user_id, name, email, gender, age)
            VALUES (%s, %s, %s, 'M', 25)
        """, (user_id, f"Auto_{user_id[-6:]}", f"{user_id}@auto.com"))
        
        logger.info(f"사용자 자동 생성: {user_id}")
        return user_id
    except Exception as e:
        logger.error(f"사용자 처리 실패: {e}")
        return user_id

# =====================================
# 주요 API 라우트들
# =====================================

@app.route('/')
def home():
    """홈페이지"""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>쇼핑몰 API</title></head>
    <body>
        <h1>쇼핑몰 API 서버</h1>
        <p>JSON과 Form 데이터를 모두 지원함</p>
        <ul>
            <li><a href="/products">상품 목록</a></li>
            <li><a href="/cart/view">장바구니</a></li>
            <li><a href="/reviews">리뷰 목록</a></li>
        </ul>
    </body>
    </html>
    """
    resp = make_response(html)
    session_id = create_session()
    resp.set_cookie('session_id', session_id, max_age=86400)
    return resp

@app.route('/add_user', methods=['POST'])
def add_user():
    """사용자 등록"""
    try:
        data = get_request_data()
        
        user_id = data.get('user_id')
        name = data.get('name')
        email = data.get('email')
        gender = data.get('gender')
        age = data.get('age')
        
        logger.info(f"사용자 등록 요청: {user_id}")
        
        if not all([user_id, name, email, gender, age]):
            return jsonify({"error": "필수 필드 누락"}), 400
        
        safe_execute("""
            INSERT INTO users (user_id, name, email, gender, age)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, name, email, gender, age))
        
        safe_execute("""
            INSERT INTO users_logs (user_id, event_type)
            VALUES (%s, 'CREATED')
        """, (user_id,))
        
        logger.info(f"사용자 생성 완료: {user_id}")
        return jsonify({"success": True, "user_id": user_id}), 201
        
    except mysql.connector.IntegrityError:
        return jsonify({"error": "이미 존재하는 사용자"}), 409
    except Exception as e:
        logger.error(f"사용자 생성 에러: {e}")
        return jsonify({"error": "사용자 생성 실패"}), 500

@app.route('/login', methods=['POST'])
def login():
    """로그인"""
    try:
        data = get_request_data()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id 필요"}), 400
        
        logger.info(f"로그인 요청: {user_id}")
        
        user_id = ensure_user_exists(user_id)
        session_id = create_session()
        
        safe_execute("""
            UPDATE sessions 
            SET user_id = %s, login_time = NOW()
            WHERE session_id = %s
        """, (user_id, session_id))
        
        resp = make_response(jsonify({
            "success": True,
            "user_id": user_id,
            "session_id": session_id
        }))
        
        resp.set_cookie('user_id', user_id, max_age=86400)
        resp.set_cookie('session_id', session_id, max_age=86400)
        
        logger.info(f"로그인 완료: {user_id}")
        return resp
        
    except Exception as e:
        logger.error(f"로그인 에러: {e}")
        return jsonify({"error": "로그인 실패"}), 500

@app.route('/cart/add', methods=['GET', 'POST'])
def add_to_cart():
    """장바구니 추가 - cart_logs 기록 포함"""
    try:
        if request.method == 'GET':
            product_id = request.args.get('id')
            quantity = int(request.args.get('quantity', 1))
            price = float(request.args.get('price', 50.0))
        else:
            data = get_request_data()
            product_id = data.get('id') or data.get('product_id')
            quantity = int(data.get('quantity', 1))
            price = float(data.get('price', 50.0))
        
        if not product_id:
            return jsonify({"error": "product_id 필요"}), 400
        
        logger.info(f"장바구니 추가: {product_id}, 수량: {quantity}")
        
        session_id = request.cookies.get('session_id')
        if not session_id:
            session_id = create_session()
        
        user_id = request.cookies.get('user_id')
        if not user_id:
            user_id = f"guest_{session_id[:8]}"
        
        user_id = ensure_user_exists(user_id)
        
        # 기존 장바구니 확인
        existing = safe_execute("""
            SELECT cart_id, quantity FROM cart
            WHERE session_id = %s AND product_id = %s
        """, (session_id, product_id), fetch=True)
        
        if existing:
            # 기존 항목 업데이트
            cart_id, old_quantity = existing[0]
            new_quantity = old_quantity + quantity
            
            safe_execute("""
                UPDATE cart SET quantity = %s, price = %s
                WHERE cart_id = %s
            """, (new_quantity, price, cart_id))
            
            # cart_logs 기록 - 업데이트
            safe_execute("""
                INSERT INTO cart_logs (cart_id, session_id, user_id, product_id, 
                                     old_quantity, new_quantity, price, event_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'UPDATED')
            """, (cart_id, session_id, user_id, product_id, old_quantity, new_quantity, price))
            
            logger.info(f"장바구니 업데이트 및 로그 기록: {product_id}")
        else:
            # 새 항목 추가
            safe_execute("""
                INSERT INTO cart (session_id, user_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, user_id, product_id, quantity, price))
            
            # 새로 추가된 cart_id 조회
            new_cart = safe_execute("""
                SELECT cart_id FROM cart 
                WHERE session_id = %s AND product_id = %s
                ORDER BY cart_id DESC LIMIT 1
            """, (session_id, product_id), fetch=True)
            
            if new_cart:
                cart_id = new_cart[0][0]
                
                # cart_logs 기록 - 추가
                safe_execute("""
                    INSERT INTO cart_logs (cart_id, session_id, user_id, product_id, 
                                         old_quantity, new_quantity, price, event_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'ADDED')
                """, (cart_id, session_id, user_id, product_id, 0, quantity, price))
                
                logger.info(f"장바구니 추가 및 로그 기록: {product_id}")
        
        resp = make_response(jsonify({
            "success": True,
            "product_id": product_id,
            "quantity": quantity,
            "user_id": user_id,
            "session_id": session_id
        }))
        
        resp.set_cookie('user_id', user_id, max_age=86400)
        resp.set_cookie('session_id', session_id, max_age=86400)
        
        return resp
        
    except Exception as e:
        logger.error(f"장바구니 추가 에러: {e}")
        return jsonify({"error": "장바구니 추가 실패"}), 500

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    """장바구니 제거 - cart_logs 기록 포함"""
    try:
        data = get_request_data()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({"error": "product_id 필요"}), 400
        
        session_id = request.cookies.get('session_id')
        if not session_id:
            return jsonify({"error": "세션 없음"}), 401
        
        user_id = request.cookies.get('user_id')
        if not user_id:
            user_id = f"guest_{session_id[:8]}"
        
        logger.info(f"장바구니 제거: {product_id}")
        
        # 기존 항목 정보 조회
        existing = safe_execute("""
            SELECT cart_id, quantity, price FROM cart
            WHERE session_id = %s AND product_id = %s
        """, (session_id, product_id), fetch=True)
        
        if existing:
            cart_id, old_quantity, price = existing[0]
            
            # cart_logs 기록 - 제거
            safe_execute("""
                INSERT INTO cart_logs (cart_id, session_id, user_id, product_id, 
                                     old_quantity, new_quantity, price, event_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'REMOVED')
            """, (cart_id, session_id, user_id, product_id, old_quantity, 0, price))
            
            # 장바구니에서 제거
            safe_execute("""
                DELETE FROM cart 
                WHERE session_id = %s AND product_id = %s
            """, (session_id, product_id))
            
            logger.info(f"장바구니 제거 및 로그 기록 완료: {product_id}")
            return jsonify({"success": True, "product_id": product_id})
        else:
            return jsonify({"error": "제거할 항목 없음"}), 404
        
    except Exception as e:
        logger.error(f"장바구니 제거 에러: {e}")
        return jsonify({"error": "장바구니 제거 실패"}), 500

@app.route('/cart/view')
def view_cart():
    """장바구니 조회"""
    try:
        session_id = request.cookies.get('session_id')
        if not session_id:
            return jsonify({"cart_items": [], "total": 0})
        
        items = safe_execute("""
            SELECT c.product_id, p.name, c.quantity, c.price, (c.quantity * c.price) as total
            FROM cart c
            LEFT JOIN products p ON c.product_id = p.id
            WHERE c.session_id = %s
        """, (session_id,), fetch=True)
        
        cart_items = []
        total = 0
        
        for item in items:
            cart_items.append({
                "product_id": item[0],
                "name": item[1] or f"Product {item[0]}",
                "quantity": item[2],
                "price": float(item[3]),
                "total": float(item[4])
            })
            total += float(item[4])
        
        return jsonify({
            "cart_items": cart_items,
            "total": total,
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"장바구니 조회 에러: {e}")
        return jsonify({"error": "장바구니 조회 실패"}), 500

@app.route('/checkout', methods=['POST'])
def checkout():
    """결제 처리"""
    try:
        session_id = request.cookies.get('session_id')
        if not session_id:
            return jsonify({"error": "세션 없음"}), 401
        
        user_id = request.cookies.get('user_id')
        if not user_id:
            user_id = f"guest_{session_id[:8]}"
        
        user_id = ensure_user_exists(user_id)
        
        logger.info(f"결제 요청: {user_id}")
        
        cart_items = safe_execute("""
            SELECT cart_id, product_id, quantity, price
            FROM cart WHERE session_id = %s
        """, (session_id,), fetch=True)
        
        if not cart_items:
            return jsonify({"error": "장바구니 비어있음"}), 400
        
        order_ids = []
        for cart_id, product_id, quantity, price in cart_items:
            order_id = str(uuid.uuid4())
            
            safe_execute("""
                INSERT INTO orders (order_id, user_id, session_id, product_id, price, quantity, order_time)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (order_id, user_id, session_id, product_id, price, quantity))
            
            # cart_logs 기록 - 체크아웃
            safe_execute("""
                INSERT INTO cart_logs (cart_id, session_id, user_id, product_id, 
                                     old_quantity, new_quantity, price, event_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'CHECKED_OUT')
            """, (cart_id, session_id, user_id, product_id, quantity, 0, price))
            
            order_ids.append(order_id)
        
        safe_execute("""
            DELETE FROM cart WHERE session_id = %s
        """, (session_id,))
        
        logger.info(f"결제 완료: {len(order_ids)}개 주문")
        
        return jsonify({
            "success": True,
            "order_count": len(order_ids),
            "order_ids": order_ids,
            "user_id": user_id
        })
        
    except Exception as e:
        logger.error(f"결제 에러: {e}")
        return jsonify({"error": "결제 실패"}), 500
        
@app.route('/add_review', methods=['GET', 'POST'])
def add_review():
    """
    TG 호환용 리뷰 API - 트래픽 제너레이터 완전 호환
    """
    try:
        # 1. 다중 소스 데이터 추출 (우선순위: 헤더 > URL > JSON > Form)
        data_all = {**request.args.to_dict(), **get_request_data()}
        
        # product_id 추출 (tg.py에서 params={'id': product_id}로 전달)
        product_id = (
            request.args.get('id')  # tg.py 호환성 우선
            or data_all.get('product_id')
            or data_all.get('productId')
            or request.headers.get('X-Product-Id')
        )
        
        # rating 추출 (tg.py에서 헤더와 JSON으로 전달)
        rating_raw = (
            request.headers.get('X-Review-Rating')  # tg.py 헤더 우선
            or data_all.get('rating')
            or data_all.get('review_rating')
            or data_all.get('score')
            or '5'  # 기본값
        )
        
        # user_id 추출 (tg.py에서 X-User-Id 헤더로 전달)
        user_id = (
            request.headers.get('X-User-Id')  # tg.py 헤더 우선
            or request.cookies.get('user_id')
            or data_all.get('user_id')
        )
        
        # session_id 추출 (tg.py에서 쿠키로 전달)
        session_id = (
            request.cookies.get('session_id')
            or request.headers.get('X-Session-Id')
            or data_all.get('session_id')
        )

        # 2. 필수 데이터 검증
        if not product_id:
            logger.warning("product_id 누락")
            return jsonify(
                success=False,
                error="product_id 누락",
                received_data={
                    'args': dict(request.args),
                    'headers': dict(request.headers),
                    'json': get_request_data()
                }
            ), 400

        # rating 정규화
        try:
            rating = int(float(rating_raw))
        except (ValueError, TypeError):
            rating = 5
        rating = max(1, min(rating, 5))  # 1~5 클램프

        # 3. 사용자 및 세션 처리
        if not user_id:
            # 사용자 ID가 없으면 게스트 생성
            if not session_id:
                session_id = create_session()
            user_id = f"guest_{session_id[:8]}"
            logger.info(f"게스트 사용자 생성: {user_id}")

        # 사용자 존재 확인 및 생성
        user_id = ensure_user_exists(user_id)
        
        # 세션 처리
        if not session_id:
            session_id = create_session()
        else:
            # 기존 세션 존재 확인 및 업데이트
            existing_session = safe_execute("""
                SELECT session_id FROM sessions WHERE session_id = %s
            """, (session_id,), fetch=True)
            
            if not existing_session:
                # 세션이 없으면 생성
                safe_execute("""
                    INSERT INTO sessions (session_id, user_id, created_at)
                    VALUES (%s, %s, NOW())
                """, (session_id, user_id))
                logger.info(f"새 세션 생성: {session_id}")
            else:
                # 기존 세션 업데이트
                safe_execute("""
                    UPDATE sessions 
                    SET user_id = %s, last_active = NOW()
                    WHERE session_id = %s
                """, (user_id, session_id))

        # 4. 상품 존재 확인
        existing_product = safe_execute(
            "SELECT id, name FROM products WHERE id = %s",
            (product_id,), fetch=True
        )
        if not existing_product:
            logger.warning(f"존재하지 않는 상품: {product_id}")
            return jsonify(
                success=False,
                error=f"상품 {product_id}를 찾을 수 없음",
                available_products_count=safe_execute("SELECT COUNT(*) FROM products", fetch=True)[0][0]
            ), 404

        product_name = existing_product[0][1]

        # 5. 리뷰 저장 (중복 처리)
        existing_review = safe_execute("""
            SELECT review_id FROM reviews
            WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id), fetch=True)

        if existing_review:
            # 기존 리뷰 업데이트
            review_id = existing_review[0][0]
            safe_execute("""
                UPDATE reviews
                SET rating = %s, review_time = NOW()
                WHERE review_id = %s
            """, (rating, review_id))
            action = "updated"
            logger.info(f"리뷰 업데이트: {review_id} (상품: {product_id}, 평점: {rating})")
        else:
            # 새 리뷰 생성
            review_id = str(uuid.uuid4())
            safe_execute("""
                INSERT INTO reviews (review_id, user_id, session_id, product_id, rating, review_time)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (review_id, user_id, session_id, product_id, rating))
            action = "created"
            logger.info(f"리뷰 생성: {review_id} (상품: {product_id}, 평점: {rating})")

        # 6. 성공 응답
        response_data = {
            'success': True,
            'action': action,
            'review_id': review_id,
            'product_id': product_id,
            'product_name': product_name,
            'rating': rating,
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'message': f'리뷰가 성공적으로 {action}됨'
        }

        resp = make_response(jsonify(response_data))
        
        # 쿠키 설정 (tg.py 호환성)
        resp.set_cookie('user_id', user_id, max_age=86400, samesite='Lax')
        resp.set_cookie('session_id', session_id, max_age=86400, samesite='Lax')
        
        return resp, 201 if action == "created" else 200

    except mysql.connector.Error as db_error:
        logger.error(f"DB 에러 in add_review: {db_error}")
        return jsonify(
            success=False,
            error="데이터베이스 에러",
            error_type="database_error",
            details=str(db_error)
        ), 500
        
    except Exception as e:
        logger.error(f"add_review 예외: {e}")
        return jsonify(
            success=False,
            error="리뷰 처리 실패",
            error_type="internal_error", 
            details=str(e)
        ), 500


@app.route('/reviews', methods=['GET'])
def get_reviews():
    """리뷰 목록 조회"""
    try:
        product_id = request.args.get('product_id')
        limit = int(request.args.get('limit', 10))
        
        if product_id:
            reviews = safe_execute("""
                SELECT review_id, product_id, rating, comment, user_id, review_time
                FROM reviews WHERE product_id = %s
                ORDER BY review_time DESC LIMIT %s
            """, (product_id, limit), fetch=True)
        else:
            reviews = safe_execute("""
                SELECT review_id, product_id, rating, comment, user_id, review_time
                FROM reviews
                ORDER BY review_time DESC LIMIT %s
            """, (limit,), fetch=True)
        
        result = []
        for review in reviews:
            result.append({
                "review_id": review[0],
                "product_id": review[1],
                "rating": review[2],
                "comment": review[3],
                "user_id": review[4],
                "review_time": review[5].isoformat() if review[5] else None
            })
        
        return jsonify({
            "success": True,
            "reviews": result,
            "count": len(result)
        })
        
    except Exception as e:
        logger.error(f"리뷰 조회 에러: {e}")
        return jsonify({"error": "리뷰 조회 실패"}), 500

@app.route('/search')
def search():
    """검색"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({"error": "검색어 필요"}), 400
        
        session_id = request.cookies.get('session_id')
        if not session_id:
            session_id = create_session()
        
        logger.info(f"검색 요청: {query}")
        
        results = safe_execute("""
            SELECT id, name, category, price 
            FROM products 
            WHERE name LIKE %s OR category LIKE %s
            LIMIT 20
        """, (f"%{query}%", f"%{query}%"), fetch=True)
        
        safe_execute("""
            INSERT INTO search_logs (session_id, search_query, searched_at)
            VALUES (%s, %s, NOW())
        """, (session_id, query))
        
        search_results = []
        for result in results:
            search_results.append({
                "id": result[0],
                "name": result[1],
                "category": result[2],
                "price": float(result[3])
            })
        
        return jsonify({
            "query": query,
            "results": search_results,
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"검색 에러: {e}")
        return jsonify({"error": "검색 실패"}), 500

@app.route('/products')
def products():
    """상품 목록"""
    try:
        products_list = safe_execute("""
            SELECT id, name, category, price 
            FROM products 
            ORDER BY id 
            LIMIT 50
        """, fetch=True)
        
        result = []
        for product in products_list:
            result.append({
                "id": product[0],
                "name": product[1],
                "category": product[2],
                "price": float(product[3])
            })
        
        return jsonify({"products": result})
        
    except Exception as e:
        logger.error(f"상품 목록 에러: {e}")
        return jsonify({"error": "상품 목록 실패"}), 500

@app.route('/users/<user_id>/exists')
def check_user_exists(user_id):
    """사용자 존재 확인"""
    try:
        result = safe_execute("""
            SELECT user_id FROM users WHERE user_id = %s
        """, (user_id,), fetch=True)
        
        exists = len(result) > 0
        return jsonify({"exists": exists, "user_id": user_id}), 200 if exists else 404
        
    except Exception as e:
        logger.error(f"사용자 확인 에러: {e}")
        return jsonify({"error": "사용자 확인 실패"}), 500

@app.route('/delete_user', methods=['POST'])
def delete_user():
    """사용자 삭제"""
    try:
        data = get_request_data()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id 필요"}), 400
        
        safe_execute("""
            INSERT INTO users_logs (user_id, event_type)
            VALUES (%s, 'DELETED')
        """, (user_id,))
        
        rowcount = safe_execute("""
            DELETE FROM users WHERE user_id = %s
        """, (user_id,))
        
        if rowcount > 0:
            return jsonify({"success": True, "user_id": user_id})
        else:
            return jsonify({"error": "사용자 없음"}), 404
        
    except Exception as e:
        logger.error(f"사용자 삭제 에러: {e}")
        return jsonify({"error": "사용자 삭제 실패"}), 500

@app.route('/logout', methods=['POST'])
def logout():
    """로그아웃"""
    try:
        session_id = request.cookies.get('session_id')
        if session_id:
            safe_execute("""
                UPDATE sessions SET logout_time = NOW()
                WHERE session_id = %s
            """, (session_id,))
        
        resp = make_response(jsonify({"success": True}))
        resp.delete_cookie('session_id')
        resp.delete_cookie('user_id')
        return resp
        
    except Exception as e:
        logger.error(f"로그아웃 에러: {e}")
        return jsonify({"success": True})

# 추가 유틸리티 API들
@app.route('/categories')
def categories():
    """카테고리 목록"""
    try:
        categories_list = safe_execute("""
            SELECT DISTINCT category FROM products ORDER BY category
        """, fetch=True)
        
        result = [cat[0] for cat in categories_list]
        return jsonify({"categories": result})
        
    except Exception as e:
        logger.error(f"카테고리 조회 에러: {e}")
        return jsonify({"error": "카테고리 조회 실패"}), 500

@app.route('/category')
def category():
    """카테고리별 상품"""
    try:
        category_name = request.args.get('category')
        
        if not category_name:
            return jsonify({"error": "카테고리 파라미터 필요"}), 400
        
        products_list = safe_execute("""
            SELECT id, name, price FROM products 
            WHERE category = %s LIMIT 20
        """, (category_name,), fetch=True)
        
        result = []
        for product in products_list:
            result.append({
                "id": product[0],
                "name": product[1],
                "price": float(product[2])
            })
        
        return jsonify({
            "category": category_name,
            "products": result
        })
        
    except Exception as e:
        logger.error(f"카테고리별 상품 에러: {e}")
        return jsonify({"error": "카테고리별 상품 조회 실패"}), 500

@app.route('/checkout_history')
def checkout_history():
    """결제 내역 조회"""
    try:
        user_id = request.cookies.get('user_id')
        
        if not user_id:
            return jsonify({"checkout_history": []})
        
        orders = safe_execute("""
            SELECT o.order_id, p.name AS product_name, o.price, o.quantity, 
                   (o.price * o.quantity) AS total_price, o.order_time
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.id
            WHERE o.user_id = %s
            ORDER BY o.order_time DESC
            LIMIT 50
        """, (user_id,), fetch=True)
        
        result = []
        for order in orders:
            result.append({
                "order_id": order[0],
                "product_name": order[1] or "Unknown Product",
                "price": float(order[2]),
                "quantity": order[3],
                "total_price": float(order[4]),
                "order_time": order[5].isoformat() if order[5] else None
            })
        
        return jsonify({
            "user_id": user_id,
            "checkout_history": result
        })
        
    except Exception as e:
        logger.error(f"결제 내역 조회 에러: {e}")
        return jsonify({"error": "결제 내역 조회 실패"}), 500

@app.route('/health')
def health_check():
    """서버 상태 확인"""
    try:
        # DB 연결 테스트
        safe_execute("SELECT 1", fetch=True)
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        })
        
    except Exception as e:
        logger.error(f"헬스체크 에러: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
    
@app.route('/push-subscription', methods=['POST'])
def push_subscription():
    """
    외부 Push Subscription 서비스가 메시지를 POST 방식으로 보내면,
    JSON 형태의 페이로드를 DB의 push_messages 테이블에 저장
    """
    try:
        data = request.get_json()
        if not data:
            return "Invalid data format. Expected JSON payload.", 400

        # JSON 페이로드 전체를 문자열로 저장
        payload_str = json.dumps(data)

        conn = get_db_connection()
        cursor = conn.cursor()
        insert_query = "INSERT INTO push_messages (payload) VALUES (%s)"
        cursor.execute(insert_query, (payload_str,))
        conn.commit()
        cursor.close()
        conn.close()

        print(f"Received and stored message: {data}")
        return "Message received and stored successfully.", 200

    except Exception as e:
        print(f"Error while processing push message: {e}")
        return f"An error occurred: {e}", 500

@app.route('/push-messages', methods=['GET'])
def get_push_messages():
    """
    DB에 저장된 push 메시지들을 JSON 형태로 반환합니다.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        select_query = "SELECT * FROM push_messages ORDER BY received_at DESC"
        cursor.execute(select_query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # 각 row의 payload를 JSON으로 파싱한 후 평탄화 처리
        for row in rows:
            try:
                payload = json.loads(row['payload'])
                # 평탄화 로직 1: "messages" 배열에 단 하나의 항목이 있고, 그 항목에 "message" 키가 있다면
                if ("messages" in payload and isinstance(payload["messages"], list)
                        and len(payload["messages"]) == 1 and isinstance(payload["messages"][0], dict)
                        and "message" in payload["messages"][0]):
                    payload["message"] = payload["messages"][0]["message"]
                    del payload["messages"]
                # 평탄화 로직 2: payload에 "message" 키가 존재하면 내부 내용을 최상위로 병합
                if "message" in payload and isinstance(payload["message"], dict):
                    inner = payload["message"]
                    for key, value in inner.items():
                        # 기존에 같은 키가 있으면 덮어씌웁니다.
                        payload[key] = value
                    del payload["message"]
                row['payload'] = payload
            except Exception:
                pass

            # received_at이 datetime 객체라면 ISO 문자열로 변환 (CustomJSONEncoder가 적용되지 않을 경우 대비)
            if 'received_at' in row and isinstance(row['received_at'], datetime):
                row['received_at'] = row['received_at'].isoformat()

        return jsonify({"messages": rows}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"An error occurred: {e}", 500
    

# 에러 핸들러들
@app.errorhandler(400)
def handle_400(e):
    return jsonify({
        "success": False,
        "error": "잘못된 요청",
        "details": str(e)
    }), 400

@app.errorhandler(404)
def handle_404(e):
    return jsonify({
        "success": False,
        "error": "리소스를 찾을 수 없음"
    }), 404

@app.errorhandler(500)
def handle_500(e):
    logger.error(f"내부 서버 오류: {e}")
    return jsonify({
        "success": False,
        "error": "내부 서버 오류"
    }), 500

if __name__ == '__main__':
    logger.info("Flask 서버 시작...")
    app.run(host='0.0.0.0', port=8080, debug=True)

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
            \"event_id\":\"\$http_x_event_id\",\\n\
            \"event_name\":\"\$http_x_event_name\",\\n\
            \"user_id\":\"\$http_x_user_id\",\\n\
            \"session_id\":\"\$cookie_session_id\",\\n\
            \"session_index\":\"\$cookie_session_idx\",\\n\
            \"is_return_visitor\":\"\$cookie_is_return\",\\n\
            \"region\":\"\$http_x_region\",\\n\
            \"device\":\"\$http_x_device\",\\n\
            \"page_url\":\"\$scheme://\$host\$request_uri\",\\n\
            \"dwell_time_seconds\":\"\$http_x_dwell_time\",\\n\
            \"product_id\":\"\$arg_id\",\\n\
            \"quantity\":\"\$http_x_quantity\",\\n\
            \"search_term\":\"\$arg_query\",\\n\
            \"review_rating\":\"\$http_x_review_rating\",\\n\
            \"event_context\":\"\$http_x_event_context\",\\n\
            \"status\":\"\$status\",\\n\
            \"request_time\":\"\$request_time\",\\n\
            \"http_user_agent\":\"\$http_user_agent\"\\n\
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

    location ~ ^/(users/.*|push-subscription|push-messages|add_user|delete_user|login|logout|products|product|categories|category|search|cart/add|cart/remove|cart/view|checkout|checkout_history|add_review|error)$ {
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
