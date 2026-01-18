# run_project.py
import subprocess
import sys
import time


def run_project():
    print("=" * 60)
    print(" مشروع محاكاة Password Spraying")
    print("=" * 60)

    print("\n اختر خياراً:")
    print("1.  تشغيل جميع المكونات (تلقائياً)")
    print("2.   تشغيل مكون محدد")
    print("3.  خروج")

    choice = input("\n  أدخل رقم الخيار: ")

    if choice == "1":
        print("\n بدء التشغيل التلقائي...")

        print("\n1.  إنشاء قاعدة البيانات...")
        subprocess.run([sys.executable, "create_db.py"])

        print("\n2.  تشغيل الخادم...")
        # تشغيل الخادم في خلفية جديدة
        subprocess.Popen([sys.executable, "server.py"])
        time.sleep(3)  # انتظار بدء الخادم

        print("\n3.  تشغيل لوحة التحكم...")
        subprocess.Popen([sys.executable, "dashboard.py"])
        time.sleep(2)

        print("\n4.  تشغيل محاكاة الهجوم...")
        subprocess.run([sys.executable, "client.py"])

        print("\n5.   تشغيل نظام الكشف...")
        subprocess.run([sys.executable, "detection.py"])

        print("\n" + "=" * 60)
        print(" تم تشغيل جميع المكونات بنجاح!")
        print(" لوحة التحكم: http://127.0.0.1:5001")
        print("  الخادم: http://127.0.0.1:5000")
        print("=" * 60)

    elif choice == "2":
        print("\n  تشغيل مكون محدد:")
        print("1. create_db.py - إنشاء قاعدة البيانات")
        print("2. server.py - تشغيل الخادم")
        print("3. client.py - محاكاة الهجوم")
        print("4. detection.py - نظام الكشف")
        print("5. dashboard.py - لوحة التحكم")

        sub_choice = input("\n  أدخل رقم المكون: ")

        files = {
            "1": "create_db.py",
            "2": "server.py",
            "3": "client.py",
            "4": "detection.py",
            "5": "dashboard.py"
        }

        if sub_choice in files:
            print(f"\n️  تشغيل {files[sub_choice]}...")
            subprocess.run([sys.executable, files[sub_choice]])
        else:
            print(" خيار غير صحيح")

    elif choice == "3":
        print("\n مع السلامة!")

    else:
        print(" الرقم المدخل غير صحيح")


if __name__ == "__main__":
    run_project()