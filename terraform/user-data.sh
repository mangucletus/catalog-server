#!/bin/bash

# Log everything
exec > >(tee /var/log/user-data.log) 2>&1
echo "Starting user-data script at $(date)"

# Update package list
echo "Updating package list..."
apt-get update -y

# Install required packages INCLUDING PostgreSQL development headers
echo "Installing packages..."
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
    net-tools

# Install Node.js 18
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Create catalog user
echo "Creating catalog user..."
useradd -m -s /bin/bash catalog

# Create application directories
echo "Creating application directories..."
mkdir -p /opt/catalog-server/{backend,frontend}
chown -R catalog:catalog /opt/catalog-server
chmod -R 755 /opt/catalog-server

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
cd /opt/catalog-server/backend
python3 -m venv venv
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install Python packages
echo "Installing Python packages..."
pip install flask==2.3.3
pip install flask-sqlalchemy==3.0.5
pip install flask-cors==4.0.0
pip install psycopg2-binary==2.9.7
pip install python-dotenv==1.0.0
pip install gunicorn==21.2.0

# Create systemd service for catalog app
echo "Creating systemd service..."
cat > /etc/systemd/system/catalog.service << 'EOF'
[Unit]
Description=Catalog Server Flask Application
After=network.target

[Service]
Type=simple
User=catalog
Group=catalog
WorkingDirectory=/opt/catalog-server/backend
Environment=PATH=/opt/catalog-server/backend/venv/bin
ExecStart=/opt/catalog-server/backend/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Set ownership
chown -R catalog:catalog /opt/catalog-server

# Enable services but don't start yet (app files will be deployed later)
echo "Configuring services..."
systemctl daemon-reload
systemctl enable catalog
systemctl enable nginx
systemctl start nginx

# Configure nginx basic setup
echo "Configuring nginx..."
cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /opt/catalog-server/frontend;
    index index.html index.htm;

    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /products {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

systemctl restart nginx

echo "User-data script completed successfully at $(date)" >> /var/log/user-data.log
echo "Ready for application deployment" >> /var/log/user-data.log