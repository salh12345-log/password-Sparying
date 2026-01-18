from flask import Flask, request, jsonify
import json
import time
from datetime import datetime
import os
from functools import wraps
app = Flask(__name__)
with open('users_db.json', 'r') as f:
    USER_DB = json.load(f)
login_attempts = []
MAX_ATTEMPTS_PER_USER = 5
TIME_WINDOW_MINUTES = 1


def log_attempt(ip_address, username, password_attempt, status):

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'ip': ip_address,
        'username': username,
        'password_attempt': password_attempt,
        'status': status
    }
    login_attempts.append(log_entry)

    with open('login_logs.json', 'w') as f:
        json.dump(login_attempts, f, indent=2)

    return log_entry


def check_account_lockout(username, ip_address):

    recent_failures = [
        attempt for attempt in login_attempts
        if attempt['username'] == username
           and attempt['status'] == 'FAILED'
    ]
    
    if len(recent_failures) >= MAX_ATTEMPTS_PER_USER:
        return True, f"الحساب مؤقتاً بعد {MAX_ATTEMPTS_PER_USER} محاولات فاشلة"
    return False, ""


def validate_localhost(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip not in ['127.0.0.1', '::1']:
            return jsonify({'error': 'الوصول مسموح فقط من localhost'}), 403
        return f(*args, **kwargs)

    return decorated_function


@app.route('/login', methods=['POST'])
@validate_localhost
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            log_attempt(request.remote_addr, username, "N/A", "INVALID_INPUT")
            return jsonify({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}), 400

        is_locked, lock_message = check_account_lockout(username, request.remote_addr)
        if is_locked:
            log_attempt(request.remote_addr, username, password, "LOCKED")
            return jsonify({'error': lock_message}), 423

        if username in USER_DB and USER_DB[username] == password:
            status = "SUCCESS"
            message = "تم تسجيل الدخول بنجاح"
            http_status = 200
        else:
            status = "FAILED"
            message = "بيانات الاعتماد غير صحيحة"
            http_status = 401

        log_attempt(request.remote_addr, username, password, status)

        return jsonify({
            'message': message,
            'username': username,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }), http_status

    except Exception as e:
        return jsonify({'error': f'خطأ في الخادم: {str(e)}'}), 500


@app.route('/logs', methods=['GET'])
@validate_localhost
def get_logs():
    return jsonify({
        'total_attempts': len(login_attempts),
        'logs': login_attempts[-100:]
    })


@app.route('/stats', methods=['GET'])
@validate_localhost
def get_stats():
    if not login_attempts:
        return jsonify({'message': 'لا توجد سجلات بعد'})

    ip_stats = {}
    for attempt in login_attempts:
        ip = attempt['ip']
        if ip not in ip_stats:
            ip_stats[ip] = {
                'total_attempts': 0,
                'failed': 0,
                'success': 0,
                'unique_users': set(),
                'first_seen': attempt['timestamp'],
                'last_seen': attempt['timestamp']
            }

        ip_stats[ip]['total_attempts'] += 1
        if attempt['status'] == 'SUCCESS':
            ip_stats[ip]['success'] += 1
        elif attempt['status'] == 'FAILED':
            ip_stats[ip]['failed'] += 1

        ip_stats[ip]['unique_users'].add(attempt['username'])
        ip_stats[ip]['last_seen'] = attempt['timestamp']

    for ip in ip_stats:
        ip_stats[ip]['unique_users'] = list(ip_stats[ip]['unique_users'])
        ip_stats[ip]['unique_users_count'] = len(ip_stats[ip]['unique_users'])

    return jsonify(ip_stats)


if __name__ == '__main__':
    if not os.path.exists('login_logs.json'):
        with open('login_logs.json', 'w') as f:
            json.dump([], f)

    print("=" * 50)
    print(" بدء تشغيل الخادم على http://127.0.0.1:5000")
    print("=" * 50)
    print(" نقاالنهاية المتاحة:")
    print("  POST http://127.0.0.1:5000/login")
    print("  GET  http://127.0.0.1:5000/logs")
    print("  GET  http://127.0.0.1:5000/stats")
    print("=" * 50)

    app.run(host='127.0.0.1', port=5000, debug=True)
