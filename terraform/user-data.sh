#!/bin/bash

# Log everything for debugging
exec > >(tee /var/log/user-data.log) 2>&1
echo "=== Starting user-data script at $(date) ==="

# Update package list
echo "=== Updating package list ==="
apt-get update -y

# Install required packages
echo "=== Installing packages ==="
apt-get install -y \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    postgresql-client \
    libpq-dev \
    python3-dev \
    build-essential \
    git \
    curl \
    net-tools \
    htop \
    unzip

# Install Node.js 18 (required for React build)
echo "=== Installing Node.js 18 ==="
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Verify installations
echo "=== Verifying installations ==="
python3 --version
pip3 --version
node --version
npm --version
nginx -v

# Create catalog user for running the application
echo "=== Creating catalog user ==="
useradd -m -s /bin/bash catalog
usermod -aG sudo catalog

# Create application directories with correct permissions
echo "=== Creating application directories ==="
mkdir -p /opt/catalog-server/{backend,frontend}
chown -R catalog:catalog /opt/catalog-server
chmod -R 755 /opt/catalog-server

# Set up Python virtual environment for the backend
echo "=== Setting up Python virtual environment ==="
cd /opt/catalog-server/backend
sudo -u catalog python3 -m venv venv
sudo -u catalog /opt/catalog-server/backend/venv/bin/pip install --upgrade pip

# Pre-install Python packages to speed up deployment
echo "=== Pre-installing Python packages ==="
sudo -u catalog /opt/catalog-server/backend/venv/bin/pip install \
    flask==2.3.3 \
    flask-sqlalchemy==3.0.5 \
    flask-cors==4.0.0 \
    psycopg2-binary \
    python-dotenv==1.0.0 \
    gunicorn==21.2.0 \
    requests \
    flask-migrate

# Create a basic placeholder app.py (will be replaced during deployment)
echo "=== Creating placeholder Flask app ==="
cat > /opt/catalog-server/backend/app.py << 'EOF'
from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'message': 'Placeholder app running, waiting for deployment',
        'timestamp': str(__import__('datetime').datetime.now())
    })

@app.route('/products')
def products():
    return jsonify({
        'success': True,
        'data': [],
        'message': 'Placeholder endpoint, waiting for deployment'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

# Create systemd service file for the catalog application
echo "=== Creating systemd service ==="
cat > /etc/systemd/system/catalog.service << 'EOF'
[Unit]
Description=Catalog Server Flask Application
After=network.target postgresql.service
Wants=network-online.target

[Service]
Type=simple
User=catalog
Group=catalog
WorkingDirectory=/opt/catalog-server/backend
Environment=PATH=/opt/catalog-server/backend/venv/bin
Environment=FLASK_ENV=production
Environment=PYTHONPATH=/opt/catalog-server/backend
EnvironmentFile=-/opt/catalog-server/backend/.env
ExecStart=/opt/catalog-server/backend/venv/bin/python app.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF

# Set ownership for the backend
chown -R catalog:catalog /opt/catalog-server/backend

# Configure nginx with a basic setup
echo "=== Configuring nginx ==="
# Remove default nginx site
rm -f /etc/nginx/sites-enabled/default

# Create basic nginx configuration (will be updated during deployment)
cat > /etc/nginx/sites-available/catalog-server << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /opt/catalog-server/frontend;
    index index.html index.htm;

    server_name _;

    # Serve static frontend files
    location / {
        try_files $uri $uri/ /index.html;
        
        # Add basic security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }

    # Proxy backend API requests
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /products {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location ~ ^/products/ {
        proxy_pass http://127.0.0.1:5000$request_uri;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /categories {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Logging
    access_log /var/log/nginx/catalog_access.log;
    error_log /var/log/nginx/catalog_error.log;
}
EOF

# Enable the nginx site
ln -sf /etc/nginx/sites-available/catalog-server /etc/nginx/sites-enabled/

# Test nginx configuration
echo "=== Testing nginx configuration ==="
nginx -t

# Create a basic index.html for frontend (will be replaced during deployment)
echo "=== Creating placeholder frontend ==="
mkdir -p /opt/catalog-server/frontend
cat > /opt/catalog-server/frontend/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalog Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #f5f7fa;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .status {
            color: #2563eb;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .message {
            color: #6b7280;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="status">🚀 Catalog Server</h1>
        <p class="message">Server is ready for deployment.<br>Frontend application will be available shortly.</p>
        <p><small>This placeholder will be replaced during deployment.</small></p>
    </div>
</body>
</html>
EOF

# Set proper ownership for frontend
chown -R www-data:www-data /opt/catalog-server/frontend
chmod -R 755 /opt/catalog-server/frontend

# Enable and start services
echo "=== Enabling and starting services ==="
systemctl daemon-reload
systemctl enable nginx
systemctl enable catalog

# Start nginx first
systemctl start nginx
sleep 2

# Start catalog service
systemctl start catalog
sleep 5

# Check service status
echo "=== Checking service status ==="
echo "Nginx status:"
systemctl is-active nginx && echo "✅ Nginx is running" || echo "❌ Nginx failed to start"

echo "Catalog service status:"
systemctl is-active catalog && echo "✅ Catalog service is running" || echo "❌ Catalog service failed to start"

# Show service logs for debugging
echo "=== Recent catalog service logs ==="
journalctl -u catalog --no-pager -n 10

# Test local connectivity
echo "=== Testing local connectivity ==="
sleep 3
curl -s http://localhost/health && echo "✅ Health endpoint accessible" || echo "❌ Health endpoint not accessible"
curl -s http://localhost/ && echo "✅ Frontend accessible" || echo "❌ Frontend not accessible"

# Database connection info (template variables will be substituted)
echo "=== Database Configuration ==="
echo "Database Host: ${db_host}"
echo "Database Name: ${db_name}"
echo "Database User: ${db_username}"
echo "Note: Database connection will be configured during application deployment"

# Create database connection test script
cat > /opt/catalog-server/backend/test_db.py << 'EOF'
#!/usr/bin/env python3
import psycopg2
import os
import sys

def test_db_connection():
    try:
        # Database connection parameters
        db_host = "${db_host}"
        db_name = "${db_name}"
        db_user = "${db_username}"
        db_password = "${db_password}"
        
        # Attempt connection
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=10
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)
EOF

chown catalog:catalog /opt/catalog-server/backend/test_db.py
chmod +x /opt/catalog-server/backend/test_db.py

# Create deployment status file
echo "=== Creating deployment status ==="
cat > /opt/catalog-server/deployment-status.json << EOF
{
    "status": "ready_for_deployment",
    "timestamp": "$(date -Iseconds)",
    "services": {
        "nginx": "$(systemctl is-active nginx)",
        "catalog": "$(systemctl is-active catalog)"
    },
    "database": {
        "host": "${db_host}",
        "name": "${db_name}",
        "user": "${db_username}"
    },
    "versions": {
        "python": "$(python3 --version)",
        "node": "$(node --version)",
        "nginx": "$(nginx -v 2>&1)"
    }
}
EOF

echo "=== User-data script completed successfully at $(date) ==="
echo "✅ Server is ready for application deployment"
echo "📝 Check deployment status: cat /opt/catalog-server/deployment-status.json"
echo "📋 View logs: tail -f /var/log/user-data.log"