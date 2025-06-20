from flask import Flask, request, Response
import json
import pymysql
from dbutils.pooled_db import PooledDB
import jwt
import datetime
import bcrypt
import os
from dotenv import load_dotenv
from functools import wraps

# 加载环境变量
load_dotenv()

app = Flask(__name__)
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')

# 创建连接池
db_pool = PooledDB(
    creator=pymysql,
    maxconnections=20,
    mincached=5,
    host=os.getenv('DB_HOST', '120.79.10.51'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER', '正确用户名'),
    password=os.getenv('DB_PASSWORD', '正确密码'),
    database=os.getenv('DB_NAME', 'app_db'),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)


# 辅助函数
def json_response(data, status=200):
    """返回JSON格式的响应"""
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        mimetype='application/json'
    )


def hash_password(password):
    """使用bcrypt哈希密码"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def check_password(password, hashed):
    """验证密码与哈希是否匹配"""
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed)


def create_token(username):
    """创建JWT令牌"""
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get('username')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """JWT认证装饰器"""

    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return json_response({"message": "用户未认证"}, 401)

        token = auth_header.split(" ")[1]
        username = verify_token(token)
        if not username:
            return json_response({"message": "无效或过期的令牌"}, 401)

        return f(username, *args, **kwargs)

    return decorated


# 数据库操作辅助函数
def execute_query(query, params=None, fetchone=False):
    """执行SQL查询"""
    conn = db_pool.connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetchone:
                return cursor.fetchone()
            return cursor.fetchall()
    finally:
        conn.close()


def execute_update(query, params=None):
    """执行更新操作"""
    conn = db_pool.connection()
    try:
        with conn.cursor() as cursor:
            affected_rows = cursor.execute(query, params or ())
            conn.commit()
            return affected_rows
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# 路由处理
@app.route('/')
def index():
    """根路由"""
    return json_response({
        "message": "欢迎使用门禁系统API",
        "endpoints": {
            "register": {"method": "POST", "description": "用户注册"},
            "login": {"method": "POST", "description": "用户登录"},
            "door": {"method": "GET", "description": "门禁控制"}
        }
    })


@app.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return json_response({"message": "请求体必须为JSON格式"}, 400)

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # 输入验证
        if not username or not password:
            return json_response({"message": "用户名和密码不能为空"}, 400)

        if len(username) < 4 or len(username) > 20:
            return json_response({"message": "用户名长度必须在4-20个字符之间"}, 400)

        if len(password) < 6:
            return json_response({"message": "密码长度不能少于6个字符"}, 400)

        # 密码哈希处理
        hashed_password = hash_password(password)

        # 检查用户名是否已存在
        existing_user = execute_query(
            "SELECT id FROM userinfo_team6 WHERE username = %s",
            (username,),
            fetchone=True
        )

        if existing_user:
            return json_response({"message": "用户名已存在"}, 409)

        # 创建新用户
        execute_update(
            "INSERT INTO userinfo_team6 (username, password) VALUES (%s, %s)",
            (username, hashed_password.decode('utf-8'))
        )

        return json_response({"message": "注册成功"})

    except Exception as e:
        app.logger.error(f"注册错误: {str(e)}")
        return json_response({"message": "服务器内部错误"}, 500)


@app.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 检查请求是否为JSON格式
        if not request.is_json:
            return json_response({"message": "请求体必须为JSON格式"}, 400)

        data = request.get_json()
        if not data:
            return json_response({"message": "请求体必须为JSON格式"}, 400)

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return json_response({"message": "用户名和密码不能为空"}, 400)

        # 查询用户
        user = execute_query(
            "SELECT password FROM userinfo_team6 WHERE username = %s",
            (username,),
            fetchone=True
        )

        if user and check_password(password, user['password']):
            token = create_token(username)
            return json_response({
                "message": "登录成功",
                "token": token,
                "expires_in": 7200  # 2小时
            })
        else:
            return json_response({"message": "用户名或密码错误"}, 401)

    except Exception as e:
        app.logger.error(f"登录错误: {str(e)}")
        return json_response({"message": "服务器内部错误"}, 500)


@app.route('/door', methods=['GET'])
@token_required
def door(username):
    """门禁控制"""
    try:
        open_value = request.args.get('open')
        if open_value == '1':
            return json_response({"message": f"{username} 开门成功"})
        elif open_value == '2':
            return json_response({"message": f"{username} 关门成功"})
        else:
            return json_response({"message": "参数错误，请使用 open=1 或 open=2"}, 400)
    except Exception as e:
        app.logger.error(f"门禁控制错误: {str(e)}")
        return json_response({"message": "服务器内部错误"}, 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
