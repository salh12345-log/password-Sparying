
import json
import time
from collections import defaultdict
from datetime import datetime


# إعدادات نظام الكشف

LOG_FILE = "auth_logs.json"
ALERT_THRESHOLD_ATTEMPTS = 5      # عدد المحاولات
ALERT_THRESHOLD_USERS = 3         # عدد المستخدمين المختلفين
TIME_WINDOW = 60                  # بالثواني


# كلاس نظام الكشف

class PasswordSprayingDetector:
    def __init__(self):
        self.attempts = defaultdict(list)

    def load_logs(self):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(" ملف السجلات غير موجود")
            return []

    def analyze_logs(self, logs):
        print("\n بدء تحليل محاولات تسجيل الدخول...\n")

        for log in logs:
            ip = log["ip"]
            user = log["username"]
            timestamp = log["timestamp"]

            self.attempts[ip].append((user, timestamp))

        self.detect_attacks()

    def detect_attacks(self):
        for ip, records in self.attempts.items():
            users = set()
            times = []

            for user, ts in records:
                users.add(user)
                times.append(ts)

            times.sort()
            duration = times[-1] - times[0] if len(times) > 1 else 0

            if (
                len(records) >= ALERT_THRESHOLD_ATTEMPTS and
                len(users) >= ALERT_THRESHOLD_USERS and
                duration <= TIME_WINDOW
            ):
                self.raise_alert(ip, len(records), len(users), duration)

    def raise_alert(self, ip, attempts, users, duration):
        print("تحذير أمني ")
        print(f" نوع الهجوم      : Password Spraying")
        print(f" عنوان IP        : {ip}")
        print(f" عدد المحاولات   : {attempts}")
        print(f" عدد المستخدمين : {users}")
        print(f" الزمن           : {duration} ثانية")
        print(f" وقت الاكتشاف    : {datetime.now()}")
        print("-" * 50)


# تشغيل نظام الكشف

def main():
    detector = PasswordSprayingDetector()
    logs = detector.load_logs()

    if logs:
        detector.analyze_logs(logs)
    else:
        print(" لا توجد بيانات لتحليلها")

if __name__ == "__main__":
    main()
