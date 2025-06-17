#!/bin/bash

# User data script to set up the catalog server on EC2 instance
# This script runs when the EC2 instance is first launched

# Exit on any error
set -e

# Log all output to a file for debugging
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting catalog server setup..."

# Update system packages
echo "Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
apt-get install -y \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    postgresql-client \
    git \
    curl \
    unzip

# Install Node.js for frontend build
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/catalog-server
cd /opt/catalog-server

# Create catalog user
echo "Creating catalog user..."
useradd -r -s /bin/false catalog || true

# Set up backend directory
echo "Setting up backend..."
mkdir -p backend
cd backend

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install \
    flask==2.3.3 \
    flask-sqlalchemy==3.0.5 \
    flask-cors==4.0.0 \
    psycopg2-binary==2.9.7 \
    python-dotenv==1.0.0 \
    gunicorn==21.2.0

# Create backend configuration
cat > config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    CORS_ORIGINS = ["*"]  # Allow all origins for simplicity
EOF

# Create models file
cat > models.py << 'EOF'
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    stock_quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url
        }
EOF

# Create main application file
cat > app.py << 'EOF'
from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Product
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        return jsonify({
            'success': True,
            'data': [product.to_dict() for product in products],
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({'success': True, 'data': product.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@app.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('price'):
            return jsonify({'success': False, 'error': 'Name and price required'}), 400
        
        new_product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            category=data.get('category', ''),
            stock_quantity=data.get('stock_quantity', 0),
            image_url=data.get('image_url', '')
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': new_product.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    try:
        products = Product.query.filter_by(category=category).all()
        return jsonify({
            'success': True,
            'data': [product.to_dict() for product in products],
            'count': len(products)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def create_sample_data():
    sample_products = [
        {'name': 'Laptop Pro', 'description': 'High-performance laptop', 'price': 1299.99, 'category': 'Electronics', 'stock_quantity': 15, 'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300'},
        {'name': 'Smartphone X', 'description': 'Latest smartphone', 'price': 899.99, 'category': 'Electronics', 'stock_quantity': 25, 'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300'},
        {'name': 'Coffee Maker', 'description': 'Automatic coffee maker', 'price': 129.99, 'category': 'Home', 'stock_quantity': 8, 'image_url': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=300'},
        {'name': 'Running Shoes', 'description': 'Comfortable running shoes', 'price': 89.99, 'category': 'Sports', 'stock_quantity': 30, 'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300'}
    ]
    
    for product_data in sample_products:
        existing = Product.query.filter_by(name=product_data['name']).first()
        if not existing:
            product = Product(**product_data)
            db.session.add(product)
    
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

# Create environment file with database connection
cat > .env << EOF
DATABASE_URL=postgresql://${db_username}:${db_password}@${db_host}:5432/${db_name}
SECRET_KEY=your-super-secret-key-$(openssl rand -hex 16)
FLASK_ENV=production
EOF

# Create systemd service file for Flask app
cat > /etc/systemd/system/catalog.service << EOF
[Unit]
Description=Catalog API Server
After=network.target

[Service]
Type=exec
User=catalog
Group=catalog
WorkingDirectory=/opt/catalog-server/backend
Environment=PATH=/opt/catalog-server/backend/venv/bin
ExecStart=/opt/catalog-server/backend/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Set up nginx configuration
cat > /etc/nginx/sites-available/catalog << 'EOF'
server {
    listen 80;
    server_name _;

    # Serve static files for frontend
    location / {
        root /opt/catalog-server/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Flask backend
    location /api/ {
        rewrite ^/api(/.*)$ $1 break;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Direct access to backend (for development)
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /products {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/catalog /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Set permissions
chown -R catalog:catalog /opt/catalog-server

# Wait for database to be ready
echo "Waiting for database to be ready..."
cd /opt/catalog-server/backend
source venv/bin/activate

# Test database connection
for i in {1..30}; do
    if python3 -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
conn.close()
print('Database connected successfully')
" 2>/dev/null; then
        echo "Database is ready!"
        break
    else
        echo "Waiting for database... attempt $i/30"
        sleep 10
    fi
done

# Initialize database
echo "Initializing database..."
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized')
"

# Create sample data
echo "Creating sample data..."
python3 -c "
from app import app, create_sample_data
with app.app_context():
    create_sample_data()
    print('Sample data created')
"

# Start and enable services
echo "Starting services..."
systemctl daemon-reload
systemctl enable catalog
systemctl start catalog
systemctl enable nginx
systemctl restart nginx

echo "Catalog server setup completed successfully!"
echo "Backend API is running on port 5000"
echo "Nginx is serving on port 80"

# Show service status
systemctl status catalog --no-pager
systemctl status nginx --no-pager