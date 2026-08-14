"""
Advanced health check for all services
"""

import requests
import redis
import psycopg2
import sys
import websocket

def check_api():
    try:
        response = requests.get("https://api.adx-shares.com/api/v1/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_database():
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="adx_prod_db",
            user="adx_prod_user",
            password="CHANGE_ME_STRONG_PASSWORD"
        )
        conn.close()
        return True
    except:
        return False

def check_redis():
    try:
        r = redis.Redis(host="redis", port=6379, password="CHANGE_ME_REDIS_PASSWORD")
        return r.ping()
    except:
        return False

def check_websocket():
    try:
        ws = websocket.create_connection("wss://api.adx-shares.com/ws/market", timeout=5)
        ws.close()
        return True
    except:
        return False

if __name__ == "__main__":
    results = {
        "API": check_api(),
        "Database": check_database(),
        "Redis": check_redis(),
        "WebSocket": check_websocket(),
    }
    
    print("\n📊 Service Status:")
    for service, status in results.items():
        status_text = "✅ Healthy" if status else "❌ Unhealthy"
        print(f"  {service}: {status_text}")
    
    if all(results.values()):
        print("\n🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("\n⚠️ Some services are unhealthy, check logs.")
        sys.exit(1)