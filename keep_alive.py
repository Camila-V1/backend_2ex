#!/usr/bin/env python3
"""
Keep-alive service para mantener Render despierto
Hace ping cada 5 minutos
"""
import requests
import time
from datetime import datetime

BACKEND_URL = 'https://backend-2ex-ecommerce.onrender.com/api/products/'
INTERVAL = 300  # 5 minutos

def ping():
    """Hace ping al backend"""
    try:
        start = time.time()
        response = requests.get(BACKEND_URL, timeout=30)
        elapsed = time.time() - start
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if response.status_code == 200:
            print(f"✅ [{timestamp}] Backend OK - {elapsed:.2f}s")
        else:
            print(f"⚠️ [{timestamp}] Backend {response.status_code} - {elapsed:.2f}s")
    
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"❌ [{timestamp}] Error: {str(e)}")

if __name__ == '__main__':
    print("🔄 Keep-alive service iniciado")
    print(f"🎯 Target: {BACKEND_URL}")
    print(f"⏱️ Intervalo: {INTERVAL}s ({INTERVAL/60}min)\n")
    
    while True:
        ping()
        time.sleep(INTERVAL)
