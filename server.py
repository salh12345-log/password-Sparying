from flask import Flask, request, jsonify
import json
import time
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)


# تحميل قاعدة البيانات
def load_user_database():
    """تحميل قاعدة بيانات المستخدمين"""
    try:
        with open('data/users_db.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(" لم يتم العثور على قاعدة البيانات")
        return {}


USER_DB = load_user_database()
login_attempts = []

# إعدادات الأمان
SECURITY_CONFIG = {
    'max_attempts_per_user': 3,
    'time_window_minutes': 2,
    'lockout_duration_minutes': 5,
    'response_delay_seconds': 0.5  # تأخير للدفاع
}


def log_attempt(ip_address, username, password_attempt, status, response_time=0):
    """تسجيل محاولة الدخول"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'ip': ip_address,
        'username': username,
        'password_attempt': password_attempt,
        'status': status,
        'response_time': response_time
    }
    login_attempts.append(log_entry)

    # حفظ في ملف السجلات
    with open('data/attack_logs.json', 'w', encoding='utf-8') as f:
        json.dump(login_attempts, f, indent=2, ensure_ascii=False)

    return log_entry


def check_security_rules(username, ip_address):
    """التحقق من قواعد الأمان"""
    # حساب المحاولات الفاشلة الأخيرة للمستخدم
    recent_failures = [
        attempt for attempt in login_attempts
        if attempt['username'] == username
           and attempt['status'] == 'FAILED'
    ]

    if len(recent_failures) >= SECURITY_CONFIG['max_attempts_per_user']:
        return False, f" الحساب مؤقتاً بعد {SECURITY_CONFIG['max_attempts_per_user']} محاولات فاشلة"

    return True, ""


def validate_localhost(f):
    """التحقق من أن الطلب من localhost فقط"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        allowed_ips = ['127.0.0.1', '::1']

        if client_ip not in allowed_ips:
            return jsonify({
                'error': ' الوصول مسموح فقط من localhost',
                'allowed_ips': allowed_ips
            }), 403

        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['POST'])
@validate_localhost
def login():
    """نقطة نهاية تسجيل الدخول"""
    start_time = time.time()

    try:
        # الحصول على البيانات
        data = request.get_json()
        if not data:
            return jsonify({'error': ' البيانات مطلوبة بصيغة JSON'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # التحقق من المدخلات
        if not username or not password:
            log_attempt(request.remote_addr, username, "N/A", "INVALID_INPUT")
            return jsonify({'error': ' اسم المستخدم وكلمة المرور مطلوبان'}), 400

        # التحقق من قواعد الأمان
        is_allowed, security_message = check_security_rules(username, request.remote_addr)
        if not is_allowed:
            log_attempt(request.remote_addr, username, password, "LOCKED")
            return jsonify({'error': security_message}), 423

        # تأخير للدفاع
        time.sleep(SECURITY_CONFIG['response_delay_seconds'])

        # التحقق من بيانات الاعتماد
        response_time = time.time() - start_time

        if username in USER_DB:
            user_data = USER_DB[username]
            if user_data['password'] == password:
                status = "SUCCESS"
                message = f" تم تسجيل الدخول بنجاح كـ {user_data['role']}"
                http_status = 200
            else:
                status = "FAILED"
                message = " كلمة المرور غير صحيحة"
                http_status = 401
        else:
            status = "FAILED"
            message = " المستخدم غير موجود"
            http_status = 401

        # تسجيل المحاولة
        log_attempt(request.remote_addr, username, password, status, response_time)

        # إرجاع النتيجة
        return jsonify({
            'message': message,
            'username': username,
            'status': status,
            'response_time': f"{response_time:.3f} ثانية",
            'timestamp': datetime.now().isoformat(),
            'server_time': response_time
        }), http_status

    except Exception as e:
        error_time = time.time() - start_time
        return jsonify({
            'error': f' خطأ في الخادم: {str(e)}',
            'response_time': f"{error_time:.3f} ثانية"
        }), 500


@app.route('/logs', methods=['GET'])
@validate_localhost
def get_logs():
    """الحصول على سجلات الدخول"""
    return jsonify({
        'total_attempts': len(login_attempts),
        'successful_attempts': len([a for a in login_attempts if a['status'] == 'SUCCESS']),
        'failed_attempts': len([a for a in login_attempts if a['status'] == 'FAILED']),
        'locked_attempts': len([a for a in login_attempts if a['status'] == 'LOCKED']),
        'logs': login_attempts[-50:]  # آخر 50 محاولة
    })


@app.route('/security-status', methods=['GET'])
@validate_localhost
def security_status():
    """حالة الأمان الحالية"""
    return jsonify({
        'security_config': SECURITY_CONFIG,
        'current_stats': {
            'total_users': len(USER_DB),
            'active_attempts': len(login_attempts),
            'unique_attackers': len(set(a['ip'] for a in login_attempts)),
            'system_load': len(login_attempts) / max(len(USER_DB), 1)
        }
    })


@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>خادم المصادقة</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; background: #f0f2f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .status { background: #2ecc71; color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; }
            .endpoint { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
            code { background: #2c3e50; color: #ecf0f1; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1> خادم المصادقة</h1>
            <p><span class="status"> نشط</span></p>
            <p>الخادم يعمل على: <code>http://127.0.0.1:5000</code></p>

            <h3> نقاط النهاية المتاحة:</h3>
            <div class="endpoint">
                <strong>POST /login</strong> - تسجيل الدخول<br>
                <small>المعطيات: {"username": "admin", "password": "Winter2024!"}</small>
            </div>
            <div class="endpoint">
                <strong>GET /logs</strong> - سجلات المحاولات
            </div>
            <div class="endpoint">
                <strong>GET /security-status</strong> - حالة الأمان
            </div>

            <h3> إعدادات الأمان:</h3>
            <ul>
                <li>الحد الأقصى للمحاولات: 3</li>
                <li>نافذة زمنية: دقيقتان</li>
                <li>تأخير الاستجابة: 0.5 ثانية</li>
                <li>مسموح فقط من: localhost</li>
            </ul>
        </div>
    </body>
    </html>
    '''


def init_server():
    """تهيئة الخادم"""
    # إنشاء مجلد data إذا لم يكن موجوداً
    if not os.path.exists('data'):
        os.makedirs('data')

    # تهيئة ملف السجلات
    if not os.path.exists('data/attack_logs.json'):
        with open('data/attack_logs.json', 'w', encoding='utf-8') as f:
            json.dump([], f)

    print("=" * 60)
    print(" بدء تشغيل خادم المصادقة")
    print("=" * 60)
    print(" العنوان: http://127.0.0.1:5000")
    print(" محمي بـ: localhost فقط")
    print(" قاعدة بيانات: " + str(len(USER_DB)) + " مستخدم")
    print("=" * 60)


if __name__ == '__main__':
    init_server()
    app.run(host='127.0.0.1', port=5000, debug=True)