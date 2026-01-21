
from flask import Flask, request, jsonify
import json
from datetime import datetime, timedelta
from functools import wraps
import os

app = Flask(__name__)


USER_DB_FILE = "users_db.json"
LOG_FILE = "login_logs.json"

MAX_FAILED_ATTEMPTS = 5        # عدد المحاولات الفاشلة قبل القفل
LOCKOUT_DURATION_MIN = 3       # مدة القفل بالدقائق


# تحميل قاعدة بيانات المستخدمين
with open(USER_DB_FILE, "r", encoding="utf-8") as f:
    USER_DB = json.load(f)

# إنشاء ملف السجلات إن لم يكن موجودًا
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)



def load_logs():
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_logs(logs):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)


def log_attempt(ip, username, status, reason=""):
    logs = load_logs()
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "ip": ip,
        "username": username,
        "status": status,
        "reason": reason
    })
    save_logs(logs)


def is_account_locked(username):
    """
    التحقق من قفل الحساب بناءً على عدد المحاولات الفاشلة
    ضمن نافذة زمنية محددة
    """
    logs = load_logs()
    failures = [
        log for log in logs
        if log["username"] == username and log["status"] == "FAILED"
    ]

    if len(failures) < MAX_FAILED_ATTEMPTS:
        return False

    last_failure_time = datetime.fromisoformat(failures[-1]["timestamp"])
    return datetime.now() - last_failure_time < timedelta(minutes=LOCKOUT_DURATION_MIN)


def localhost_only(func):
    """
    السماح بالوصول من localhost فقط (بيئة اختبار آمنة)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return jsonify({"error": "Access allowed from localhost only"}), 403
        return func(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["POST"])
@localhost_only
def login():
    data = request.get_json()
    ip = request.remote_addr

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        log_attempt(ip, username, "INVALID_INPUT", "Missing username or password")
        return jsonify({"error": "Username and password are required"}), 400

    if is_account_locked(username):
        log_attempt(ip, username, "LOCKED", "Account temporarily locked")
        return jsonify({"error": "Account temporarily locked"}), 423

    if USER_DB.get(username) == password:
        log_attempt(ip, username, "SUCCESS", "Valid credentials")
        return jsonify({
            "message": "Login successful",
            "username": username,
            "timestamp": datetime.now().isoformat()
        }), 200

    log_attempt(ip, username, "FAILED", "Invalid credentials")
    return jsonify({"message": "Invalid username or password"}), 401


@app.route("/health", methods=["GET"])
def health_check():
    """
    Endpoint بسيط للتحقق من حالة الخادم
    """
    return jsonify({
        "status": "running",
        "time": datetime.now().isoformat()
    })



if __name__ == "__main__":
    print("=" * 60)
    print(" Authentication Server Running")
    print(" URL: http://127.0.0.1:5000")
    print(" Environment: Localhost Only (Safe Simulation)")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
