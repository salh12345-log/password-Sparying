# detection.py
import json
from collections import defaultdict
from datetime import datetime, timedelta


class SimpleDetector:
    def __init__(self):
        self.logs = self.load_logs()

    def load_logs(self):
        try:
            with open('login_logs.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def detect_spraying(self):
        print("🛡  نظام كشف هجمات رش كلمات المرور")
        print("=" * 50)

        if not self.logs:
            print(" لا توجد سجلات للتحليل")
            return

        # تحليل حسب IP
        ip_activity = defaultdict(list)

        for log in self.logs:
            ip = log.get('ip', 'unknown')
            ip_activity[ip].append(log)

        for ip, logs in ip_activity.items():
            # حساب عدد المستخدمين المختلفين
            unique_users = set(log.get('username') for log in logs)

            # حساب الزمن بين أول وآخر محاولة
            if len(logs) >= 2:
                first_time = datetime.fromisoformat(logs[0]['timestamp'])
                last_time = datetime.fromisoformat(logs[-1]['timestamp'])
                time_diff = (last_time - first_time).total_seconds() / 60  # بالدقائق
            else:
                time_diff = 0

            print(f"\n عنوان IP: {ip}")
            print(f"    عدد المستخدمين المختلفين: {len(unique_users)}")
            print(f"    إجمالي المحاولات: {len(logs)}")
            print(f"     الفترة الزمنية: {time_diff:.1f} دقيقة")

            # قاعدة الكشف: إذا حاول على أكثر من 3 مستخدمين في أقل من 5 دقائق
            if len(unique_users) >= 3 and time_diff < 5:
                print("   ⚠  **تم اكتشاف هجوم Password Spraying محتمل!**")
                print("    المستخدمين: " + ", ".join(list(unique_users)[:5]))
            else:
                print("    نشاط طبيعي")

        print("\n" + "=" * 50)


if __name__ == '__main__':
    detector = SimpleDetector()
    detector.detect_spraying()