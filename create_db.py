import json 
import hashlib

users = {
    "admin": "Winter2024!",
    "john.doe": "Summer2023!",
    "jane.smith": "Spring2024!",
    "mike.brown": "Autumn2023!",
    "sara.jones": "Password123!",
    "alex.wang": "Welcome2024!",
    "lisa.chen": "P@ssw0rd",
    "tom.harris": "Admin@123",
    "emily.davis": "SecurePass!",
    "david.lee": "Changeme2024!"
}

with open('users_db.json', 'w') as f:
    json.dump(users, f, indent=2)


print(" تم إنشاء قاعدة بيانات المستخدمين في users_db.json")
