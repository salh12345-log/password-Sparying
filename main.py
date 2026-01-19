import subprocess
import sys
import time
import threading
import webbrowser
import os


def print_header():
    """طباعة ترويسة المشروع"""
    print("\n" + "=" * 70)
    print(" مشروع محاكاة هجوم Password Spraying مع نظام دفاع ذكي")
    print("=" * 70)
    print(" لوحة تحكم تفاعلية تعرض الهجوم والدفاع في الوقت الفعلي")
    print("=" * 70)


def check_requirements():
    """التحقق من تثبيت المتطلبات"""
    print("\n التحقق من المتطلبات...")

    requirements = ['flask', 'requests']
    missing = []

    for req in requirements:
        try:
            __import__(req.replace('-', '_'))
            print(f"    {req}")
        except ImportError:
            print(f"    {req}")
            missing.append(req)

    if missing:
        print(f"\n  المتطلبات الناقصة: {', '.join(missing)}")
        print("   قم بالتثبيت: pip install flask requests")
        return False

    print(" جميع المتطلبات مثبتة")
    return True


def run_component(component_name, command):
    """تشغيل مكون من المشروع"""
    print(f"\n تشغيل: {component_name}")
    print(f" الأمر: {command}")
    print("-" * 40)

    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # قراءة الإخراج في الوقت الحقيقي
        for line in process.stdout:
            print(f"   {line.strip()}")

        process.wait()
        return process.returncode == 0
    except Exception as e:
        print(f"    خطأ: {e}")
        return False


def run_all_components():
    """تشغيل جميع المكونات"""
    print("\n بدء التشغيل الكامل للمشروع...")

    # 1. إنشاء قاعدة البيانات
    print("\n1.  إنشاء قاعدة البيانات...")
    run_component("قاعدة البيانات", f"{sys.executable} create_database.py")

    # 2. تشغيل الخادم في خيط منفصل
    print("\n2. 🖥️  تشغيل خادم المصادقة...")
    server_thread = threading.Thread(
        target=lambda: run_component("الخادم", f"{sys.executable} server.py"),
        daemon=True
    )
    server_thread.start()
    time.sleep(3)  # انتظار بدء الخادم

    # 3. تشغيل لوحة التحكم في خيط منفصل
    print("\n3.  تشغيل لوحة التحكم...")
    dashboard_thread = threading.Thread(
        target=lambda: run_component("لوحة التحكم", f"{sys.executable} dashboard.py"),
        daemon=True
    )
    dashboard_thread.start()
    time.sleep(2)

    # 4. فتح المتصفح تلقائياً
    print("\n4.  فتح لوحة التحكم في المتصفح...")
    webbrowser.open("http://127.0.0.1:5001")

    print("\n" + "=" * 70)
    print(" تم تشغيل جميع المكونات بنجاح!")
    print("=" * 70)
    print("\n الآن يمكنك:")
    print("1. فتح نافذة طرفية جديدة")
    print("2. تشغيل محاكاة الهجوم: python attack_simulator.py")
    print("3. تشغيل نظام الدفاع: python defense_system.py")
    print("4. مشاهدة لوحة التحكم: http://127.0.0.1:5001")
    print("\n روابط النظام:")
    print("    لوحة التحكم: http://127.0.0.1:5001")
    print("   🖥️  الخادم: http://127.0.0.1:5000")
    print("\n  اضغط Ctrl+C في أي نافذة لإيقاف المكون")
    print("=" * 70)


def run_single_component():
    """تشغيل مكون محدد"""
    print("\n  تشغيل مكون محدد:")
    print("1.  create_database.py - إنشاء قاعدة البيانات")
    print("2.   server.py - خادم المصادقة")
    print("3.  attack_simulator.py - محاكاة الهجوم")
    print("4.  defense_system.py - نظام الدفاع")
    print("5.  dashboard.py - لوحة التحكم")
    print("0.   رجوع")

    try:
        choice = input("\n  أدخل رقم المكون: ").strip()
    except KeyboardInterrupt:
        print("\n\n مع السلامة!")
        return

    components = {
        "1": ("قاعدة البيانات", "create_database.py"),
        "2": ("الخادم", "server.py"),
        "3": ("محاكاة الهجوم", "attack_simulator.py"),
        "4": ("نظام الدفاع", "defense_system.py"),
        "5": ("لوحة التحكم", "dashboard.py")
    }

    if choice in components:
        name, file = components[choice]
        run_component(name, f"{sys.executable} {file}")

        # إذا كان لوحة التحكم، افتح المتصفح
        if choice == "5":
            time.sleep(2)
            webbrowser.open("http://127.0.0.1:5001")
    elif choice == "0":
        return
    else:
        print(" خيار غير صحيح")


def cleanup_files():
    """تنظيف الملفات القديمة"""
    print("\n تنظيف الملفات القديمة...")

    files_to_clean = [
        'data/users_db.json',
        'data/attack_logs.json',
        'data/defense_logs.json',
        'data/attack_results.json'
    ]

    cleaned = 0
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"     حذف {file}")
            cleaned += 1

    if cleaned > 0:
        print(f" تم تنظيف {cleaned} ملف")
    else:
        print(" لا توجد ملفات للتنظيف")


def show_instructions():
    """عرض تعليمات الاستخدام"""
    print("\n" + "=" * 70)
    print(" دليل الاستخدام السريع")
    print("=" * 70)

