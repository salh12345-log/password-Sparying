from flask import Flask, render_template_string, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# قالب HTML مبسط
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم الهجوم</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: white; padding: 20px; }
        .container { max-width: 1200px; margin: auto; }
        .header { text-align: center; padding: 30px; background: #16213e; border-radius: 15px; margin-bottom: 30px; }
        h1 { color: #0ea5e9; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-box { background: #0f3460; padding: 20px; border-radius: 10px; text-align: center; }
        .stat-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
        .red { color: #ef4444; }
        .green { color: #10b981; }
        .yellow { color: #f59e0b; }
        .blue { color: #3b82f6; }
        .attack-log { background: #1e293b; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid; }
        .success { border-left-color: #10b981; }
        .failed { border-left-color: #ef4444; }
        .locked { border-left-color: #f59e0b; }
        .btn { background: #0ea5e9; color: white; padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; margin: 20px auto; display: block; }
        .btn:hover { background: #0284c7; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ لوحة تحكم نظام الهجوم والدفاع</h1>
            <p>مراقبة محاولات الهجوم في الوقت الفعلي</p>
        </div>

        <div class="stats">
            <div class="stat-box">
                <div>إجمالي المحاولات</div>
                <div class="stat-value blue">{{ attack_stats.total_attempts }}</div>
                <div>محاولة دخول</div>
            </div>

            <div class="stat-box">
                <div>المحاولات الناجحة</div>
                <div class="stat-value {% if attack_stats.successful_attempts > 0 %}red{% else %}green{% endif %}">
                    {{ attack_stats.successful_attempts }}
                </div>
                <div>محاولة</div>
            </div>

            <div class="stat-box">
                <div>الحسابات المقفلة</div>
                <div class="stat-value yellow">{{ attack_stats.locked_accounts }}</div>
                <div>حساب</div>
            </div>

            <div class="stat-box">
                <div>نسبة النجاح</div>
                <div class="stat-value {% if attack_stats.success_rate > 20 %}red{% else %}green{% endif %}">
                    {{ attack_stats.success_rate|round(1) }}%
                </div>
                <div>من إجمالي المحاولات</div>
            </div>
        </div>

        {% if recent_attacks %}
        <div style="background: #16213e; padding: 25px; border-radius: 15px; margin-bottom: 30px;">
            <h2 style="color: #0ea5e9; margin-bottom: 20px;">🔍 آخر محاولات الهجوم</h2>
            {% for attack in recent_attacks %}
            <div class="attack-log {{ 'success' if attack.status == 'SUCCESS' else 'failed' if attack.status == 'FAILED' else 'locked' }}">
                <div style="display: flex; justify-content: space-between;">
                    <strong>{{ attack.username }}</strong>
                    <span style="opacity: 0.8;">{{ attack.timestamp[11:19] }}</span>
                </div>
                <div>كلمة المرور: <code>{{ attack.password_attempt }}</code></div>
                <div style="margin-top: 8px;">
                    {% if attack.status == 'SUCCESS' %}
                    <span style="color: #10b981;">✅ نجحت</span>
                    {% elif attack.status == 'FAILED' %}
                    <span style="color: #ef4444;">❌ فشلت</span>
                    {% else %}
                    <span style="color: #f59e0b;">🔒 مقفلة</span>
                    {% endif %}
                    • ⏱️ {{ attack.response_time }} ثانية • 🌐 {{ attack.ip }}
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div style="text-align: center; padding: 50px; background: #16213e; border-radius: 15px;">
            <div style="font-size: 4em; margin-bottom: 20px;">📭</div>
            <h3 style="color: #0ea5e9;">لا توجد محاولات هجوم حالية</h3>
            <p>قم بتشغيل attack_simulator.py لبدء محاكاة الهجوم</p>
        </div>
        {% endif %}

        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #0f3460; border-radius: 10px;">
            <h3 style="color: #0ea5e9; margin-bottom: 15px;">📋 تعليمات التشغيل</h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; text-align: right;">
                <div>1. شغل الخادم: <code>python server.py</code></div>
                <div>2. شغل الهجوم: <code>python attack_simulator.py</code></div>
                <div>3. شغل الدفاع: <code>python defense_system.py</code></div>
                <div>4. شاهد النتائج هنا!</div>
            </div>
        </div>

        <button class="btn" onclick="location.reload()">🔄 تحديث الصفحة</button>

        <div style="text-align: center; margin-top: 30px; color: #94a3b8; font-size: 0.9em;">
            آخر تحديث: {{ current_time }}
            {% if attack_stats.total_attempts > 0 and attack_stats.successful_attempts > 0 %}
            <div style="color: #ef4444; margin-top: 10px; font-weight: bold;">
                ⚠️ تحذير: تم اكتشاف محاولات ناجحة!
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''


def load_dashboard_data():
    """تحميل بيانات لوحة التحكم بدون بيانات دفاع"""
    try:
        # تحميل سجلات الهجوم
        with open('data/attack_logs.json', 'r', encoding='utf-8') as f:
            attack_logs = json.load(f)
    except:
        attack_logs = []

    # حساب إحصائيات الهجوم فقط
    attack_stats = {
        'total_attempts': len(attack_logs),
        'successful_attempts': len([a for a in attack_logs if a.get('status') == 'SUCCESS']),
        'failed_attempts': len([a for a in attack_logs if a.get('status') == 'FAILED']),
        'locked_accounts': len([a for a in attack_logs if a.get('status') == 'LOCKED']),
        'unique_ips': len(set(a.get('ip', '') for a in attack_logs)),
        'success_rate': 0
    }

    if attack_stats['total_attempts'] > 0:
        attack_stats['success_rate'] = (attack_stats['successful_attempts'] / attack_stats['total_attempts']) * 100

    # تحضير آخر عمليات الهجوم للعرض
    recent_attacks = []
    for log in attack_logs[-15:]:  # آخر 15 محاولة
        recent_attacks.append({
            'username': log.get('username', 'غير معروف'),
            'password_attempt': log.get('password_attempt', ''),
            'status': log.get('status', 'UNKNOWN'),
            'timestamp': log.get('timestamp', ''),
            'response_time': f"{log.get('response_time', 0):.3f}",
            'ip': log.get('ip', '')
        })

    return {
        'attack_stats': attack_stats,
        'recent_attacks': recent_attacks,
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


@app.route('/')
def dashboard():
    """عرض لوحة التحكم الرئيسية"""
    data = load_dashboard_data()
    return render_template_string(DASHBOARD_TEMPLATE, **data)


@app.route('/api/attack-stats')
def api_attack_stats():
    """واجهة API لإحصائيات الهجوم"""
    data = load_dashboard_data()
    return jsonify(data['attack_stats'])


@app.route('/health')
def health():
    """فحص صحة الخادم"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'password-spraying-dashboard'
    })


def init_dashboard():
    """تهيئة لوحة التحكم"""
    # إنشاء مجلد data إذا لم يكن موجوداً
    if not os.path.exists('data'):
        os.makedirs('data')
        print("📁 تم إنشاء مجلد data")

    # تهيئة ملف السجلات إذا لم يكن موجوداً
    if not os.path.exists('data/attack_logs.json'):
        with open('data/attack_logs.json', 'w', encoding='utf-8') as f:
            json.dump([], f)

    print("=" * 60)
    print("📊 بدء تشغيل لوحة التحكم")
    print("=" * 60)
    print("🌐 العنوان: http://127.0.0.1:5001")
    print("📱 افتح المتصفح وشاهد النتائج")
    print("=" * 60)


if __name__ == '__main__':
    init_dashboard()
    app.run(host='127.0.0.1', port=5001, debug=False)