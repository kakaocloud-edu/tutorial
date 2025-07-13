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

cat > $APP_DIR/app.py <<'EOL'
from flask import Flask, request, make_response, jsonify
import uuid, time, random, mysql.connector, json
from datetime import datetime
from mysql.connector import Error
from flask.json import JSONEncoder
from decimal import Decimal

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

DB_CONFIG = {
    'user': 'admin',
    'password': 'admin1234',
    'host': '${MYSQL_HOST}',
    'database': 'shopdb',
    'ssl_disabled': True
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.before_request
def update_last_active():
    session_id = request.cookies.get('session_id')
    if session_id:
        try:
            conn = get_db_connection()
            cur  = conn.cursor()
            cur.execute(
                "UPDATE sessions SET last_active = NOW() WHERE session_id = %s",
                (session_id,)
            )
            conn.commit()
        except Exception as e:
            print(f"Failed to update last_active: {e}")
        finally:
            cur and cur.close()
            conn and conn.close()

def respond_html_or_json(data, html_renderer):
    accept = request.headers.get("Accept", "")
    if "application/json" in accept:
        return jsonify(data)
    else:
        return html_renderer(data)

def get_or_create_session_id():
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        try:
            conn = get_db_connection()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO sessions (session_id) VALUES (%s)",
                (session_id,)
            )
            conn.commit()
        finally:
            cur and cur.close()
            conn and conn.close()
    return session_id

# ─── 요청 파라미터를 통합해서 읽어오는 헬퍼 ─────────────────────────────────
def get_request_data():
    """
    JSON body > form data > query string 순으로 값을 읽어옵니다.
    """
    data = request.get_json(silent=True) or {}
    data.update(request.form.to_dict())
    for key, val in request.args.items():
        data[key] = val
    return data
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    endpoints = {
        "Home": {"url": "/", "description": "메인 페이지로 이동"},
        "Products": {"url": "/products", "description": "상품 목록 확인"},
        "Product Detail": {"url": "/product?id=101", "description": "상품 상세 (id 필요)"},
        "Search": {"url": "/search?query=Bluetooth", "description": "검색 (query 필요)"},
        "Checkout History": {"url": "/checkout_history", "description": "결제 내역 확인"},
        "Categories": {"url": "/categories", "description": "카테고리 목록"},
        "Category": {"url": "/category?name=Electronics", "description": "카테고리별 상품"},
        "View Cart": {"url": "/cart/view", "description": "장바구니 조회"},
        "Trigger Error": {"url": "/error", "description": "테스트용 오류 발생"}
    }

    html = "<h1>Online Shopping Mall</h1><p>테스트 환경입니다.</p><hr>"
    html += "<h2>GET Endpoints</h2><ul>"
    for name, info in endpoints.items():
        html += f"<li><a href='{info['url']}'>{name}</a>: {info['description']}</li>"
    html += "</ul>"

    html += """
    <h2>POST Endpoints</h2>
    <h3>Register</h3>
    <form action="/add_user" method="post">
      <input name="user_id" value="test_user" required>
      <input name="name"    value="Test User" required>
      <input name="email"   value="test@example.com" required>
      <input name="gender"  value="M" required>
      <input name="age"     value="30" required>
      <button>Register</button>
    </form>
    <h3>Unregister</h3>
    <form action="/delete_user" method="post">
      <input name="user_id" value="test_user" required>
      <button>Unregister</button>
    </form>
    <h3>Login</h3>
    <form action="/login" method="post">
      <input name="user_id" value="u1" required>
      <button>Login</button>
    </form>
    <h3>Logout</h3>
    <form action="/logout" method="post"><button>Logout</button></form>
    <h3>Add to Cart</h3>
    <form action="/cart/add" method="post">
      <input name="id" value="101" required>
      <input name="quantity" type="number" min="1" value="1" required>
      <button>Add to Cart</button>
    </form>
    <h3>Remove from Cart</h3>
    <form action="/cart/remove" method="post">
      <input name="product_id" value="101" required>
      <input name="quantity" type="number" min="1" value="1" required>
      <button>Remove</button>
    </form>
    <h3>Checkout</h3>
    <form action="/checkout" method="post"><button>Checkout</button></form>
    <h3>Add Review</h3>
    <form action="/add_review" method="post">
      <input name="product_id" value="101" required>
      <input name="rating" type="number" min="1" max="5" value="5" required>
      <button>Add Review</button>
    </form>
    """
    resp = make_response(html)
    resp.set_cookie('session_id', get_or_create_session_id())
    return resp

@app.route('/users/<user_id>/exists', methods=['GET'])
def check_user_exists(user_id):
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
        exists = cur.fetchone() is not None
        return jsonify({"exists": exists, "user_id": user_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/push-subscription', methods=['POST'])
def push_subscription():
    try:
        data = request.get_json()
        if not data:
            return "Invalid JSON", 400
        payload = json.dumps(data)
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("INSERT INTO push_messages(payload) VALUES(%s)", (payload,))
        conn.commit()
        return "Stored", 200
    except Exception as e:
        return str(e), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/push-messages', methods=['GET'])
def get_push_messages():
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM push_messages ORDER BY received_at DESC")
        rows = cur.fetchall()
        for row in rows:
            try:
                p = json.loads(row['payload'])
                # 평탄화 로직...
                row['payload'] = p
            except: pass
            if isinstance(row.get('received_at'), datetime):
                row['received_at'] = row['received_at'].isoformat()
        return jsonify({"messages": rows}), 200
    except Exception as e:
        return str(e), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/add_user', methods=['POST'])
def add_user():
    data    = get_request_data()
    user_id = data.get('user_id')
    name    = data.get('name')
    email   = data.get('email')
    gender  = data.get('gender')
    age     = data.get('age')
    if not all([user_id, name, email, gender, age]):
        return "All fields required", 400
    if gender not in ['F','M']:
        return "Gender M/F", 400
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id=%s",(user_id,))
        if cur.fetchone():
            return "Exists", 409
        cur.execute(
            "INSERT INTO users(user_id,name,email,gender,age) VALUES(%s,%s,%s,%s,%s)",
            (user_id,name,email,gender,age)
        )
        cur.execute("INSERT INTO users_logs(user_id,event_type) VALUES(%s,'CREATED')",(user_id,))
        conn.commit()
        return "Created", 201
    except Exception as e:
        return str(e), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/delete_user', methods=['POST'])
def delete_user():
    data    = get_request_data()
    user_id = data.get('user_id')
    if not user_id:
        return "user_id required", 400
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id=%s",(user_id,))
        if not cur.fetchone():
            return "Not found", 404
        cur.execute("INSERT INTO users_logs(user_id,event_type) VALUES(%s,'DELETED')",(user_id,))
        cur.execute(
            "UPDATE sessions SET logout_time=NOW() WHERE user_id=%s AND logout_time IS NULL",
            (user_id,)
        )
        cur.execute("DELETE FROM users WHERE user_id=%s",(user_id,))
        conn.commit()
        return "Deleted", 200
    except Exception as e:
        return str(e), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/login', methods=['POST'])
def login():
    data    = get_request_data()
    user_id = data.get('user_id')
    old_uid = request.cookies.get('user_id')
    old_sid = request.cookies.get('session_id')
    if not user_id:
        return "user_id required", 400
    if old_uid == user_id:
        return f"Already {user_id}", 200
    if old_uid and old_uid != user_id:
        try:
            conn = get_db_connection()
            cur  = conn.cursor()
            cur.execute("UPDATE sessions SET logout_time=NOW() WHERE session_id=%s",(old_sid,))
            conn.commit()
        finally:
            cur and cur.close()
            conn and conn.close()
        sid = get_or_create_session_id()
    else:
        sid = get_or_create_session_id()
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE user_id=%s",(user_id,))
        user = cur.fetchone()
        if not user:
            return "Not found", 404
        cur.execute(
            "UPDATE sessions SET user_id=%s, login_time=NOW() WHERE session_id=%s",
            (user_id, sid)
        )
        conn.commit()
        resp = make_response(f"Logged in {user_id}")
        resp.set_cookie('user_id', user_id)
        resp.set_cookie('session_id', sid)
        return resp
    except Exception as e:
        return str(e), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    sid = request.cookies.get('session_id')
    if sid:
        try:
            conn = get_db_connection()
            cur  = conn.cursor()
            cur.execute("UPDATE sessions SET logout_time=NOW() WHERE session_id=%s",(sid,))
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            cur and cur.close()
            conn and conn.close()
    resp = make_response("Logged out")
    resp.delete_cookie('session_id')
    resp.delete_cookie('user_id')
    return resp

@app.route('/search')
def search():
    query = request.args.get('query','').strip()
    sid   = get_or_create_session_id()
    if not query:
        return "query required", 400
    if not sid:
        return "No session", 400
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT session_id FROM sessions WHERE session_id=%s",(sid,))
        if not cur.fetchone():
            return "Invalid session", 400
        cur.execute(
            "SELECT id,name FROM products WHERE name LIKE %s OR category LIKE %s",
            (f"%{query}%",f"%{query}%")
        )
        rows = cur.fetchall()
        cur.execute(
            "INSERT INTO search_logs(session_id,search_query,searched_at) VALUES(%s,%s,NOW())",
            (sid, query)
        )
        conn.commit()
        data = {
            "query": query,
            "results": [{"id":r["id"],"name":r["name"]} for r in rows]
        }
        return respond_html_or_json(data, lambda d: "<ul>" + "".join(f"<li>{i['name']}</li>" for i in d["results"]) + "</ul>")
    except Exception as e:
        return str(e), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/products')
def products():
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT p.id,p.name,p.category,
                   CASE WHEN COUNT(r.review_id)=0 THEN NULL ELSE AVG(r.rating) END AS avg_rating
            FROM products p
            LEFT JOIN reviews r ON p.id=r.product_id
            GROUP BY p.id
        """)
        rows = cur.fetchall()
        def render(d):
            return "<ul>" + "".join(f"<li>{r['name']}</li>" for r in d) + "</ul>"
        return respond_html_or_json(rows, render)
    except Exception as e:
        return str(e), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/product')
def product_detail():
    pid = request.args.get('id')
    sid = get_or_create_session_id()
    uid = request.cookies.get('user_id')
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT p.id,p.name,p.price,p.category,
                   CASE WHEN COUNT(r.review_id)=0 THEN NULL ELSE AVG(r.rating) END AS avg_rating
            FROM products p
            LEFT JOIN reviews r ON p.id=r.product_id
            WHERE p.id=%s
            GROUP BY p.id
        """,(pid,))
        product = cur.fetchone()
        cur.execute("""
            SELECT r.rating,r.review_time,u.name reviewer
            FROM reviews r JOIN users u ON r.user_id=u.user_id
            WHERE r.product_id=%s
            ORDER BY r.review_time DESC
        """,(pid,))
        reviews = cur.fetchall()
        cur.execute(
            "SELECT quantity FROM cart WHERE session_id=%s AND product_id=%s",
            (sid,pid)
        )
        cart_item = cur.fetchone()
        if not product:
            return "Not found", 404
        data = {
            "product": {
                "id": product["id"],
                "name": product["name"],
                "price": str(product["price"]),
                "category": product["category"],
                "avg_rating": product["avg_rating"]
            },
            "reviews": [
                {"rating":r["rating"],"time":r["review_time"].isoformat(),"by":r["reviewer"]}
                for r in reviews
            ],
            "cart_quantity": cart_item["quantity"] if cart_item else 0
        }
        def render(d):
            p=d["product"]
            return f"<h1>{p['name']}</h1><p>Price:{p['price']}</p>"
        return respond_html_or_json(data, render)
    except Exception as e:
        return str(e), 500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data       = get_request_data()
    product_id = data.get('id')
    quantity   = int(data.get('quantity',1))
    user_id    = request.cookies.get('user_id')
    session_id = get_or_create_session_id()
    if not all([product_id,user_id,session_id]):
        return "Missing params",400
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT id,price FROM products WHERE id=%s",(product_id,))
        prod = cur.fetchone()
        if not prod:
            return "Invalid product",404
        price = prod["price"]
        cur.execute(
            "SELECT cart_id,quantity FROM cart WHERE session_id=%s AND product_id=%s",
            (session_id,product_id)
        )
        item = cur.fetchone()
        if item:
            old_q = item["quantity"]
            new_q = old_q + quantity
            cur.execute(
                "UPDATE cart SET quantity=%s WHERE cart_id=%s",
                (new_q,item["cart_id"])
            )
            cur.execute("""
                INSERT INTO cart_logs
                (cart_id,session_id,user_id,product_id,old_quantity,new_quantity,price,event_type,event_time)
                VALUES(%s,%s,%s,%s,%s,%s,%s,'UPDATED',NOW())
            """,(item["cart_id"],session_id,user_id,product_id,old_q,new_q,price))
        else:
            cur.execute("""
                INSERT INTO cart(session_id,user_id,product_id,quantity,price,added_at)
                VALUES(%s,%s,%s,%s,%s,NOW())
            """,(session_id,user_id,product_id,quantity,price))
            cur.execute("SELECT LAST_INSERT_ID() AS cart_id")
            cid = cur.fetchone()["cart_id"]
            cur.execute("""
                INSERT INTO cart_logs
                (cart_id,session_id,user_id,product_id,old_quantity,new_quantity,price,event_type,event_time)
                VALUES(%s,%s,%s,%s,0,%s,%s,'ADDED',NOW())
            """,(cid,session_id,user_id,product_id,quantity,price))
        conn.commit()
        return f"Added {quantity}"
    except Exception as e:
        return str(e),500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    data               = get_request_data()
    product_id         = data.get('product_id')
    quantity_to_remove = int(data.get('quantity',0))
    session_id         = get_or_create_session_id()
    if not (product_id and quantity_to_remove>0):
        return "Invalid params",400
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT cart_id,quantity,price FROM cart WHERE session_id=%s AND product_id=%s",
            (session_id,product_id)
        )
        item = cur.fetchone()
        if not item:
            return "Not in cart",404
        old_q = item["quantity"]
        new_q = old_q - quantity_to_remove
        if new_q<=0:
            cur.execute(
                "DELETE FROM cart WHERE cart_id=%s",(item["cart_id"],)
            )
        else:
            cur.execute(
                "UPDATE cart SET quantity=%s WHERE cart_id=%s",
                (new_q,item["cart_id"])
            )
        action = 'REMOVED' if new_q<=0 else 'UPDATED'
        cur.execute("""
            INSERT INTO cart_logs
            (cart_id,session_id,user_id,product_id,old_quantity,new_quantity,price,event_type,event_time)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """,(
            item["cart_id"],session_id,request.cookies.get('user_id'),
            product_id,old_q,new_q,item["price"],action
        ))
        conn.commit()
        return f"{action}"
    except Exception as e:
        return str(e),500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/checkout', methods=['POST'])
def checkout():
    user_id    = request.cookies.get('user_id')
    session_id = get_or_create_session_id()
    if not (user_id and session_id):
        return "Missing auth",400
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT cart_id,product_id,price,quantity FROM cart WHERE session_id=%s
        """,(session_id,))
        items = cur.fetchall()
        if not items:
            return "Empty cart",200
        for it in items:
            oid = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO orders(order_id,user_id,session_id,product_id,price,quantity,order_time)
                VALUES(%s,%s,%s,%s,%s,%s,NOW())
            """,(oid,user_id,session_id,it["product_id"],it["price"],it["quantity"]))
            cur.execute("""
                INSERT INTO cart_logs
                (cart_id,session_id,user_id,product_id,old_quantity,new_quantity,price,event_type,event_time)
                VALUES(%s,%s,%s,%s,%s,0,%s,'CHECKED_OUT',NOW())
            """,(
                it["cart_id"],session_id,user_id,it["product_id"],it["quantity"],it["price"]
            ))
        cur.execute("DELETE FROM cart WHERE session_id=%s",(session_id,))
        conn.commit()
        return "Checked out"
    except Exception as e:
        return str(e),500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/checkout_history')
def checkout_history():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return "Login required",400
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT o.order_id,p.name,o.price,o.quantity,(o.price*o.quantity) AS total,o.order_time
            FROM orders o JOIN products p ON o.product_id=p.id
            WHERE o.user_id=%s
            ORDER BY o.order_time DESC
        """,(user_id,))
        rows = cur.fetchall()
        data = {
            "user_id": user_id,
            "history": [
                {"order_id":r["order_id"],"product":r["name"],"total":str(r["total"]),"time":r["order_time"].isoformat()}
                for r in rows
            ]
        }
        return respond_html_or_json(data, lambda d: "<ul>"+"".join(f"<li>{h['product']}:{h['total']}</li>" for h in d["history"])+"</ul>")
    except Exception as e:
        return str(e),500
    finally:
        cur and cur.close()
        conn and conn.close()

@app.route('/add_review', methods=['POST'])
def add_review():
    data       = get_request_data()
    product_id = data.get('product_id')
    rating     = data.get('rating')
    user_id    = request.cookies.get('user_id')
    session_id = get_or_create_session_id()
    if not all([product_id,rating,user_id,session_id]):
        return "Missing params",400
    try:
        conn = get_db_connection()
        cur  = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM products WHERE id=%s",(product_id,))
        if not cur.fetchone():
            return "Invalid product",404
        cur.execute("SELECT session_id FROM sessions WHERE session_id=%s",(session_id,))
        if not cur.fetchone():
            return "Invalid session",400
        cur.execute("SELECT user_id FROM users WHERE user_id=%s",(user_id,))
        if not cur.fetchone():
            return "Invalid user",400
        rid = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO reviews(review_id,product_id,rating,user_id,session_id,review_time)
            VALUES(%s,%s,%s,%s,%s,NOW())
        """,(rid,product_id,rating,user_id,session_id))
        conn.commit()
        return "Review added"
    except Exception as e:
        return str(e),500
    finally:
        cur and cur.close()
        conn and conn.close()

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
