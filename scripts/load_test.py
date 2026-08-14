"""
Load Testing with Locust
Install: pip install locust
Run: locust -f scripts/load_test.py --host=https://api.adx-shares.com
"""

from locust import HttpUser, task, between
import random

class TradingUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.token = None
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "Test@123456"
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(5)
    def view_markets(self):
        self.client.get("/api/v1/markets/assets?limit=20", headers=self.headers)

    @task(3)
    def view_crypto(self):
        self.client.get("/api/v1/crypto/list?limit=20", headers=self.headers)

    @task(2)
    def view_portfolio(self):
        self.client.get("/api/v1/trading/portfolio", headers=self.headers)

    @task(1)
    def create_order(self):
        if self.token:
            self.client.post("/api/v1/trading/orders", 
                json={
                    "asset_symbol": "BTC",
                    "side": "BUY",
                    "order_type": "MARKET",
                    "quantity": 0.001
                },
                headers=self.headers
            )