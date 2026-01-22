# detection.py
import json
from collections import defaultdict
from datetime import datetime, timedelta

LOG_FILE = "login_logs.json"

class AuthenticationBehaviorDetector:
    def __init__(self):
        self.logs = self.load_logs()

    def load_logs(self):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def analyze(self):
        print("=" * 60)
        print(" Authentication Behavior Analysis System")
        print("=" * 60)

        if not self.logs:
            print(" No login activity found.")
            return

        ip_activity = defaultdict(list)

        # تجميع المحاولات حسب IP
        for log in self.logs:
            ip = log.get("ip", "unknown")
            ip_activity[ip].append(log)

        for ip, attempts in ip_activity.items():
            usernames = set()
            failed_attempts = 0

            timestamps = [
                datetime.fromisoformat(a["timestamp"])
                for a in attempts
                if "timestamp" in a
            ]

            if timestamps:
                duration = (max(timestamps) - min(timestamps)).total_seconds() / 60
            else:
                duration = 0

            for a in attempts:
                usernames.add(a.get("username"))
                if a.get("status") == "FAILED":
                    failed_attempts += 1

            print(f"\n IP Address: {ip}")
            print(f" Total Attempts: {len(attempts)}")
            print(f" Failed Attempts: {failed_attempts}")
            print(f" Unique Usernames: {len(usernames)}")
            print(f" Time Window: {duration:.1f} minutes")

            # قاعدة كشف سلوكي (Behavior-based)
            if failed_attempts >= 5 and duration <= 10:
                print("   Suspicious authentication behavior detected")
            else:
                print("  Normal authentication behavior")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    detector = AuthenticationBehaviorDetector()
    detector.analyze()
