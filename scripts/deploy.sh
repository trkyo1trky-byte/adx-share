#!/bin/bash

set -e

echo "🚀 Starting ADX SHARES deployment to production..."

# 1. Pull latest changes
echo "📦 Pulling updates from Git..."
git pull origin main

# 2. Build and run containers
echo "🐳 Building and running Docker Compose..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Run migrations if needed
echo "🔄 Running migrations..."
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head || true

# 4. Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app.core.database import engine
from app.models import user, role, market, crypto, trading
user.Base.metadata.create_all(bind=engine)
role.Base.metadata.create_all(bind=engine)
market.Base.metadata.create_all(bind=engine)
crypto.Base.metadata.create_all(bind=engine)
trading.Base.metadata.create_all(bind=engine)
"

# 5. Restart Nginx
echo "🔄 Restarting Nginx..."
docker-compose -f docker-compose.prod.yml restart nginx

# 6. Health check
echo "✅ Verifying services..."
sleep 5
curl -s -o /dev/null -w "%{http_code}" https://api.adx-shares.com/api/v1/health | grep -q "200" && echo "✅ Backend is healthy" || echo "❌ Backend is not responding"

echo "🎉 Deployment completed successfully!"