import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import os


class IntelligentDefenseSystem:
    """نظام الدفاع المتقدم لاكتشاف ومنع هجمات رش كلمات المرور"""

    def __init__(self, attack_logs_file='data/attack_logs.json'):
        self.logs_file = attack_logs_file
        self.defense_logs = []
        self.detected_attacks = []

        # عتبات الكشف
        self.detection_thresholds = {
            'time_window_minutes': 5,
            'unique_users_threshold': 3,
            'max_attempts_per_ip': 10,
            'password_variety_threshold': 2,
            'response_time_analysis': True
        }

        # إجراءات الدفاع
        self.defense_actions = {
            'block_ip': True,
            'increase_delay': True,
            'notify_admin': True,
            'log_detailed': True
        }

    def datetime_to_string(self, dt_obj):
        """تحويل كائن datetime إلى string"""
        if isinstance(dt_obj, datetime):
            return dt_obj.isoformat()
        return str(dt_obj)

    def prepare_for_json(self, data):
        """تحضير البيانات للتخزين في JSON"""
        if isinstance(data, dict):
            return {k: self.prepare_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.prepare_for_json(item) for item in data]
        elif isinstance(data, (datetime, timedelta)):
            return self.datetime_to_string(data)
        elif isinstance(data, set):
            return list(data)
        else:
            return data

    def load_attack_logs(self):
        """تحميل سجلات الهجوم"""
        try:
            with open(self.logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                print(f" تم تحميل {len(logs)} سجل هجوم")
                return logs
        except FileNotFoundError:
            print(f"  لم يتم العثور على ملف السجلات: {self.logs_file}")
            return []
        except json.JSONDecodeError:
            print(f" خطأ في قراءة ملف السجلات")
            return []

    def analyze_ip_behavior(self, ip_address, logs):
        """تحليل سلوك عنوان IP معين"""
        ip_logs = [log for log in logs if log.get('ip') == ip_address]

        if not ip_logs:
            return None

        # تحويل التواريخ
        for log in ip_logs:
            if 'timestamp' in log:
                try:
                    log['datetime'] = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                except:
                    log['datetime'] = datetime.now()
            else:
                log['datetime'] = datetime.now()

        # ترتيب حسب الوقت
        ip_logs.sort(key=lambda x: x['datetime'])

        # استخراج التواريخ كـ strings لحساب الفرق
        first_time = ip_logs[0]['datetime']
        last_time = ip_logs[-1]['datetime']

        analysis = {
            'ip_address': ip_address,
            'total_attempts': len(ip_logs),
            'unique_users': len(set(log.get('username', '') for log in ip_logs)),
            'first_seen': first_time.isoformat(),
            'last_seen': last_time.isoformat(),
            'time_span_seconds': (last_time - first_time).total_seconds(),
            'failed_attempts': len([log for log in ip_logs if log.get('status') == 'FAILED']),
            'successful_attempts': len([log for log in ip_logs if log.get('status') == 'SUCCESS']),
            'passwords_tried': list(set(log.get('password_attempt', '') for log in ip_logs)),
            'average_response_time': 0
        }

        # حساب متوسط وقت الاستجابة
        response_times = []
        for log in ip_logs:
            if 'response_time' in log:
                try:
                    response_times.append(float(log['response_time']))
                except:
                    pass

        if response_times:
            analysis['average_response_time'] = sum(response_times) / len(response_times)

        return analysis

    def detect_spray_pattern(self, ip_analysis):
        """الكشف عن نمط رش كلمات المرور"""
        if not ip_analysis:
            return False, []

        detection_flags = []

        # 1. عدد المستخدمين المختلفين
        if ip_analysis['unique_users'] >= self.detection_thresholds['unique_users_threshold']:
            detection_flags.append(f" مستخدمين مختلفين: {ip_analysis['unique_users']}")

        # 2. عدد المحاولات الكلي
        if ip_analysis['total_attempts'] >= self.detection_thresholds['max_attempts_per_ip']:
            detection_flags.append(f" محاولات كلي: {ip_analysis['total_attempts']}")

        # 3. تنوع كلمات المرور
        if len(ip_analysis['passwords_tried']) <= self.detection_thresholds['password_variety_threshold']:
            detection_flags.append(f" تنوع كلمات مرور منخفض: {len(ip_analysis['passwords_tried'])}")

        # 4. الفترة الزمنية القصيرة
        time_window = self.detection_thresholds['time_window_minutes'] * 60
        if ip_analysis['time_span_seconds'] < time_window:
            detection_flags.append(f"  فترة زمنية قصيرة: {ip_analysis['time_span_seconds']:.0f} ثانية")

        # 5. معدل المحاولات
        if ip_analysis['time_span_seconds'] > 0:
            attempts_per_second = ip_analysis['total_attempts'] / ip_analysis['time_span_seconds']
            if attempts_per_second > 0.3:  # أكثر من محاولة كل 3 ثواني
                detection_flags.append(f" معدل محاولات مرتفع: {attempts_per_second:.2f}/ثانية")

        return len(detection_flags) >= 2, detection_flags

    def calculate_risk_score(self, ip_analysis, detection_flags):
        """حساب درجة الخطورة"""
        score = 0

        # عوامل الخطورة
        if ip_analysis['unique_users'] >= 5:
            score += 30
        elif ip_analysis['unique_users'] >= 3:
            score += 20

        if ip_analysis['total_attempts'] >= 15:
            score += 30
        elif ip_analysis['total_attempts'] >= 10:
            score += 20

        if len(ip_analysis['passwords_tried']) == 1:
            score += 25

        if ip_analysis['successful_attempts'] > 0:
            score += 15

        # تقييم بناءً على عدد علامات الكشف
        score += len(detection_flags) * 10

        return min(score, 100)

    def execute_defense_actions(self, ip_address, risk_score, attack_details):
        """تنفيذ إجراءات الدفاع"""
        actions_taken = []

        print(f"\n تنفيذ إجراءات الدفاع لـ {ip_address}")
        print("-" * 50)

        # 1. حظر IP مؤقت
        if self.defense_actions['block_ip'] and risk_score >= 60:
            actions_taken.append({
                'action': 'block_ip',
                'details': f"حظر {ip_address} لمدة 30 دقيقة",
                'timestamp': datetime.now().isoformat()
            })
            print(f" 1. حظر مؤقت لـ {ip_address}")

        # 2. زيادة تأخير الاستجابة
        if self.defense_actions['increase_delay'] and risk_score >= 40:
            delay_increase = min(risk_score / 20, 5.0)  # حتى 5 ثواني
            actions_taken.append({
                'action': 'increase_delay',
                'details': f"زيادة تأخير الاستجابة إلى {delay_increase:.1f} ثانية",
                'timestamp': datetime.now().isoformat()
            })
            print(f" 2. زيادة تأخير الاستجابة: {delay_increase:.1f} ثانية")

        # 3. تسجيل مفصل
        if self.defense_actions['log_detailed']:
            actions_taken.append({
                'action': 'detailed_logging',
                'details': f"تسجيل هجوم من {ip_address}",
                'timestamp': datetime.now().isoformat()
            })
            print(f" 3. تسجيل مفصل للهجوم")

        # 4. تنبيه المديرين
        if self.defense_actions['notify_admin'] and risk_score >= 70:
            actions_taken.append({
                'action': 'notify_admin',
                'details': f"تنبيه عن هجوم من {ip_address} (خطورة: {risk_score}%)",
                'timestamp': datetime.now().isoformat()
            })
            print(f" 4. إرسال تنبيه للمديرين")

        # 5. إجراءات إضافية بناءً على الخطورة
        if risk_score >= 80:
            actions_taken.append({
                'action': 'advanced_protection',
                'details': "تفعيل الحماية المتقدمة والمراقبة المستمرة",
                'timestamp': datetime.now().isoformat()
            })
            print(f" 5. تفعيل الحماية المتقدمة")

        print("-" * 50)
        return actions_taken

    def analyze_and_defend(self):
        """التحليل الكامل وتنفيذ الدفاع"""
        print("=" * 70)
        print("  نظام الدفاع الذكي - تحليل وتنفيذ")
        print("=" * 70)

        # تحميل السجلات
        attack_logs = self.load_attack_logs()
        if not attack_logs:
            print(" لا توجد سجلات للتحليل")
            return

        # تحليل عناوين IP الفريدة
        unique_ips = set(log.get('ip', '') for log in attack_logs if log.get('ip'))
        print(f" تحليل {len(unique_ips)} عنوان IP...")
        print(f" إجمالي السجلات: {len(attack_logs)}")

        detected_count = 0

        for ip in unique_ips:
            if not ip:  # تخطي العناوين الفارغة
                continue

            print(f"\n{'=' * 50}")
            print(f" تحليل عنوان IP: {ip}")

            # تحليل سلوك IP
            ip_analysis = self.analyze_ip_behavior(ip, attack_logs)
            if not ip_analysis:
                print("     لا توجد بيانات للتحليل")
                continue

            # عرض تحليل السلوك
            print(f"    مستخدمين مختلفين: {ip_analysis['unique_users']}")
            print(f"    إجمالي المحاولات: {ip_analysis['total_attempts']}")
            print(f"    محاولات ناجحة: {ip_analysis['successful_attempts']}")
            print(f"    محاولات فاشلة: {ip_analysis['failed_attempts']}")
            print(f"     الفترة الزمنية: {ip_analysis['time_span_seconds']:.0f} ثانية")

            passwords = ip_analysis['passwords_tried'][:3]
            if passwords:
                print(f"    كلمات مرور مجربة: {', '.join(passwords)}")
                if len(ip_analysis['passwords_tried']) > 3:
                    print(f"      + {len(ip_analysis['passwords_tried']) - 3} كلمات أخرى")

            # الكشف عن الأنماط
            is_suspicious, detection_flags = self.detect_spray_pattern(ip_analysis)

            if is_suspicious:
                detected_count += 1

                # حساب درجة الخطورة
                risk_score = self.calculate_risk_score(ip_analysis, detection_flags)

                print(f"\n  هجوم مكتشف!")
                print(f" درجة الخطورة: {risk_score}/100")

                # عرض علامات الكشف
                if detection_flags:
                    print(" علامات الكشف:")
                    for flag in detection_flags:
                        print(f"   • {flag}")

                # تنفيذ إجراءات الدفاع
                attack_details = {
                    'ip_analysis': ip_analysis,
                    'detection_flags': detection_flags,
                    'risk_score': risk_score
                }

                defense_actions = self.execute_defense_actions(ip, risk_score, attack_details)

                # حفظ الهجوم المكتشف (مع تحويل التواريخ)
                safe_ip_analysis = self.prepare_for_json(ip_analysis)

                self.detected_attacks.append({
                    'ip_address': ip,
                    'detection_time': datetime.now().isoformat(),
                    'risk_score': risk_score,
                    'ip_analysis': safe_ip_analysis,
                    'detection_flags': detection_flags,
                    'defense_actions': defense_actions,
                    'users_targeted': list(set(log.get('username', '') for log in attack_logs if log.get('ip') == ip))
                })

                # حساب فعالية الدفاع
                if ip_analysis['total_attempts'] > 0:
                    prevention_rate = (ip_analysis['failed_attempts'] / ip_analysis['total_attempts']) * 100
                    print(f"\n تقييم فعالية الدفاع:")
                    print(f"    منع {ip_analysis['failed_attempts']} من أصل {ip_analysis['total_attempts']} محاولة")
                    print(f"    معدل المنع: {prevention_rate:.1f}%")

                    if ip_analysis['time_span_seconds'] > 0:
                        attack_speed = ip_analysis['total_attempts'] / ip_analysis['time_span_seconds']
                        print(f"     سرعة الهجوم: {attack_speed:.2f} محاولة/ثانية")

                        # تقييم تأثير الدفاع على سرعة الهجوم
                        if risk_score >= 60:
                            speed_reduction = min(risk_score / 10, 80)  # حتى 80%
                            print(f"    تقليل السرعة بنسبة: {speed_reduction:.0f}%")
            else:
                print(f"\n نشاط طبيعي - لا توجد علامات هجوم")

        # عرض ملخص النتائج
        print("\n" + "=" * 70)
        print(" ملخص نتائج الدفاع")
        print("=" * 70)
        print(f" الهجمات المكتشفة: {detected_count}")

        total_defense_actions = sum(len(a.get('defense_actions', [])) for a in self.detected_attacks)
        print(f"  إجراءات دفاع منفذة: {total_defense_actions}")

        if detected_count > 0:
            avg_risk = sum(a['risk_score'] for a in self.detected_attacks) / detected_count
            print(f" متوسط درجة الخطورة: {avg_risk:.1f}/100")

            # عرض تفاصيل الهجمات
            print("\n تفاصيل الهجمات المكتشفة:")
            for i, attack in enumerate(self.detected_attacks, 1):
                print(f"\n{i}.  {attack['ip_address']} (خطورة: {attack['risk_score']}/100)")
                print(f"   ] مستخدمين مستهدفين: {len(attack['users_targeted'])}")
                print(f"    محاولات: {attack['ip_analysis']['total_attempts']}")
                print(f"    إجراءات دفاع: {len(attack['defense_actions'])}")

        # حفظ سجلات الدفاع
        self.save_defense_logs()

        print(f"\n تم حفظ سجلات الدفاع في: data/defense_logs.json")
        print("=" * 70)

    def save_defense_logs(self):
        """حفظ سجلات الدفاع"""
        defense_summary = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_attacks_detected': len(self.detected_attacks),
            'detected_attacks': self.prepare_for_json(self.detected_attacks),
            'defense_configuration': {
                'thresholds': self.detection_thresholds,
                'actions': self.defense_actions
            }
        }

        try:
            with open('data/defense_logs.json', 'w', encoding='utf-8') as f:
                json.dump(defense_summary, f, indent=2, ensure_ascii=False)
            print(" تم حفظ سجلات الدفاع بنجاح")
        except Exception as e:
            print(f" خطأ في حفظ سجلات الدفاع: {e}")
            # حفظ نسخة مبسطة
            simple_summary = {
                'total_attacks': len(self.detected_attacks),
                'timestamp': datetime.now().isoformat()
            }
            with open('data/defense_logs_simple.json', 'w', encoding='utf-8') as f:
                json.dump(simple_summary, f, indent=2, ensure_ascii=False)


def main():
    """الدالة الرئيسية"""
    # إنشاء مجلد data إذا لم يكن موجوداً
    if not os.path.exists('data'):
        os.makedirs('data')
        print(" تم إنشاء مجلد data")

    # التحقق من وجود سجلات الهجوم
    if not os.path.exists('data/attack_logs.json'):
        print(" لم يتم العثور على سجلات الهجوم")
        print("  قم بتشغيل هجوم أولاً باستخدام attack_simulator.py")
        print("\n الخطوات المطلوبة:")
        print("1. python create_database.py")
        print("2. python server.py  (في نافذة منفصلة)")
        print("3. python attack_simulator.py")
        print("4. python defense_system.py  (هذا الملف)")
        return

    # إنشاء وتشغيل نظام الدفاع
    print(" بدء نظام الدفاع الذكي...")
    defense_system = IntelligentDefenseSystem()
    defense_system.analyze_and_defend()


if __name__ == "__main__":
    main()