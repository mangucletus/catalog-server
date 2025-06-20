from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

db = SQLAlchemy(app)

# Product model (adjust according to your existing model)
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(255))
    stock_quantity = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'stock_quantity': self.stock_quantity
        }

# Health check endpoints (both with and without /api prefix)
@app.route('/health')
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Catalog server is running"
    })

# Get all products (both with and without /api prefix)
@app.route('/products')
@app.route('/api/products')
def get_products():
    try:
        products = Product.query.all()
        products_data = [product.to_dict() for product in products]
        
        return jsonify({
            "success": True,
            "data": products_data,
            "count": len(products_data)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Get single product by ID
@app.route('/products/<int:product_id>')
@app.route('/api/products/<int:product_id>')
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            "success": True,
            "data": product.to_dict()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 404

# Get products by category (NEW ROUTE - this was missing!)
@app.route('/products/category/<category>')
@app.route('/api/products/category/<category>')
def get_products_by_category(category):
    try:
        products = Product.query.filter_by(category=category).all()
        products_data = [product.to_dict() for product in products]
        
        return jsonify({
            "success": True,
            "data": products_data,
            "count": len(products_data)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Create product (admin function)
@app.route('/products', methods=['POST'])
@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            category=data.get('category'),
            image_url=data.get('image_url'),
            stock_quantity=data.get('stock_quantity', 0)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": product.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

# Initialize database with sample data
def init_sample_data():
    if Product.query.count() == 0:
        sample_products = [
            Product(
                name="Laptop Pro",
                description="High-performance laptop for professionals",
                price=1299.99,
                category="Electronics",
                image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300",
                stock_quantity=15
            ),
            Product(
                name="Smartphone X",
                description="Latest smartphone with amazing camera",
                price=899.99,
                category="Electronics",
                image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300",
                stock_quantity=25
            ),
            Product(
                name="Coffee Maker",
                description="Automatic coffee maker for perfect brew",
                price=129.99,
                category="Home",
                image_url="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=300",
                stock_quantity=8
            ),
            Product(
                name="Running Shoes",
                description="Comfortable running shoes for daily exercise",
                price=89.99,
                category="Sports",
                image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300",
                stock_quantity=30
            )
        ]
        
        for product in sample_products:
            db.session.add(product)
        db.session.commit()
        print("Sample data initialized!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    
    # For development
    app.run(host='0.0.0.0', port=5000, debug=True)