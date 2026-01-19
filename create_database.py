import json
import os
from datetime import datetime


def create_user_database():
    """إنشاء قاعدة بيانات المستخدمين مع كلمات مرور متنوعة"""

    users_data = {
        # المستخدمين مع كلمات مرور حقيقية
        "admin": {
            "password": "Winter2024!",
            "role": "Administrator",
            "created": datetime.now().isoformat()
        },
        "john.doe": {
            "password": "Summer2023!",
            "role": "User",
            "created": datetime.now().isoformat()
        },
        "jane.smith": {
            "password": "Spring2024!",
            "role": "Manager",
            "created": datetime.now().isoformat()
        },
        "mike.brown": {
            "password": "Autumn2023!",
            "role": "Developer",
            "created": datetime.now().isoformat()
        },
        "sara.jones": {
            "password": "Password123!",
            "role": "Analyst",
            "created": datetime.now().isoformat()
        },
        # مستخدمين إضافيين
        "alex.wang": {
            "password": "Welcome2024!",
            "role": "User",
            "created": datetime.now().isoformat()
        },
        "lisa.chen": {
            "password": "P@ssw0rd",
            "role": "User",
            "created": datetime.now().isoformat()
        },
        "tom.harris": {
            "password": "Admin@123",
            "role": "User",
            "created": datetime.now().isoformat()
        }
    }

    # إنشاء مجلد data إذا لم يكن موجوداً
    if not os.path.exists('data'):
        os.makedirs('data')

    # حفظ قاعدة البيانات
    with open('data/users_db.json', 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print("  قاعدة بيانات المستخدمين")
    print("=" * 60)
    print(f" تم إنشاء قاعدة بيانات تحتوي على {len(users_data)} مستخدم")
    print(" الموقع: data/users_db.json")
    print("\n قائمة المستخدمين:")
    for i, (username, data) in enumerate(users_data.items(), 1):
        print(f"   {i:2d}. {username:15} - الدور: {data['role']}")
    print("=" * 60)

    return users_data


if __name__ == "__main__":
    create_user_database()