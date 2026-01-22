# client.py (Manual Authentication Client)
import requests
import json
from datetime import datetime

SERVER_URL = "http://127.0.0.1:5000/login"

results = []

print("=" * 60)
print(" Manual Authentication Client")
print(" Enter credentials to test authentication behavior")
print(" Type 'exit' to quit")
print("=" * 60)

while True:
    username = input("\n Username: ").strip()
    if username.lower() == "exit":
        break

    password = input(" Password: ").strip()
    if password.lower() == "exit":
        break

    payload = {
        "username": username,
        "password": password
    }

    try:
        response = requests.post(
            SERVER_URL,
            json=payload,
            timeout=5
        )

        status = response.status_code
        try:
            message = response.json().get("message", "")
        except:
            message = response.text

        print(f" Status Code: {status} | Message: {message}")

        results.append({
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "status_code": status,
            "message": message
        })

    except Exception as e:
        print(f" Error: {str(e)}")
        results.append({
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "error": str(e)
        })

# حفظ جميع المحاولات
with open("manual_login_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 60)
print(" Session finished")
print(" Results saved to manual_login_results.json")
print("=" * 60)
