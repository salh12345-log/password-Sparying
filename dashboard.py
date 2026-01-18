# dashboard.py
from flask import Flask, render_template_string
import json

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>لوحة تحكم الأمان</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 10px; }
        h1 { color: #333; text-align: center; }
        .stat { background: #e3f2fd; padding: 15px; margin: 10px; border-radius: 5px; }
        .alert { background: #ffebee; color: #c62828; padding: 15px; margin: 10px; border-radius: 5px; }
        .safe { background: #e8f5e9; color: #2e7d32; padding: 15px; margin: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>️ لوحة تحكم نظام الأمان</h1>

        <div class="stat">
            <h3> الإحصائيات</h3>
            <p>إجمالي المحاولات: {{ stats.total_attempts }}</p>
            <p>العناوين IP النشطة: {{ stats.unique_ips }}</p>
            <p>الهجمات المكتشفة: {{ stats.detected_threats }}</p>
        </div>

        {% if stats.detected_threats > 0 %}
        <div class="alert">
             تم اكتشاف {{ stats.detected_threats }} هجوم مشبوه
        </div>
        {% else %}
        <div class="safe">
             النظام آمن - لا توجد هجمات مكتشفة
        </div>
        {% endif %}

        <div class="stat">
            <h3> آخر 5 محاولات</h3>
            {% for log in recent_logs %}
            <p>{{ log.timestamp[11:19] }} - {{ log.username }} - {{ log.status }} - {{ log.ip }}</p>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''


def load_data():
    try:
        with open('login_logs.json', 'r') as f:
            logs = json.load(f)

        unique_ips = set(log.get('ip') for log in logs)

        # تحليل بسيط للكشف
        detected_threats = 0
        ip_counts = {}
        for log in logs:
            ip = log.get('ip')
            ip_counts[ip] = ip_counts.get(ip, 0) + 1

        # إذا كان IP حاول على أكثر من 5 مستخدمين
        for ip, count in ip_counts.items():
            unique_users = set(log.get('username') for log in logs if log.get('ip') == ip)
            if len(unique_users) >= 3:
                detected_threats += 1

        return {
            'stats': {
                'total_attempts': len(logs),
                'unique_ips': len(unique_ips),
                'detected_threats': detected_threats
            },
            'recent_logs': logs[-5:] if logs else []
        }
    except:
        return {
            'stats': {'total_attempts': 0, 'unique_ips': 0, 'detected_threats': 0},
            'recent_logs': []
        }


@app.route('/')
def dashboard():
    data = load_data()
    return render_template_string(HTML_TEMPLATE, **data)


if __name__ == '__main__':
    print(" لوحة التحكم تعمل على http://127.0.0.1:5001")
    app.run(host='127.0.0.1', port=5001, debug=False)