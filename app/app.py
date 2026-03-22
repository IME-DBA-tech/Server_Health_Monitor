import os
import time
import pandas as pd
from flask import Flask, jsonify
import mysql.connector
import redis

app = Flask(__name__)

# الربط مع Redis
cache = redis.Redis(host=os.getenv('REDIS_HOST', 'redis'), port=6379)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'db'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

@app.route('/')
def get_metrics():
    # محاولة القراءة من الكاش أولاً
    cached_data = cache.get('infra_metrics')
    if cached_data:
        return jsonify({"source": "cache", "data": eval(cached_data)})

    # لو مش في الكاش، نقرأ من MySQL (اللي المفروض إنت ربطتها بالـ CSV)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM server_metrics")
    rows = cursor.fetchall()
    
    # تخزين في الكاش لمدة 30 ثانية
    cache.setex('infra_metrics', 30, str(rows))
    
    cursor.close()
    conn.close()
    return jsonify({"source": "database", "data": rows})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
