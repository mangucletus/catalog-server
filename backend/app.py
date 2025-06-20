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

# Product model
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

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "message": "Catalog server is running"
    }), 200

# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        # Get query parameters for potential filtering
        category = request.args.get('category')
        
        if category:
            products = Product.query.filter_by(category=category).all()
        else:
            products = Product.query.all()
        
        products_data = [product.to_dict() for product in products]
        
        return jsonify({
            "success": True,
            "data": products_data,
            "count": len(products_data)
        }), 200
        
    except Exception as e:
        print(f"Error fetching products: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch products",
            "message": str(e)
        }), 500

# Get single product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                "success": False,
                "error": "Product not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": product.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error fetching product {product_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch product",
            "message": str(e)
        }), 500

# Get products by category - IMPORTANT: This route must come AFTER /products/<int:id>
@app.route('/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    """Get products filtered by category"""
    try:
        products = Product.query.filter_by(category=category).all()
        products_data = [product.to_dict() for product in products]
        
        return jsonify({
            "success": True,
            "data": products_data,
            "count": len(products_data),
            "category": category
        }), 200
        
    except Exception as e:
        print(f"Error fetching products for category {category}: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to fetch products for category: {category}",
            "message": str(e)
        }), 500

# Create new product
@app.route('/products', methods=['POST'])
def create_product():
    """Create a new product (admin function)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('name') or not data.get('price'):
            return jsonify({
                "success": False,
                "error": "Missing required fields: name and price"
            }), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            category=data.get('category', 'Uncategorized'),
            image_url=data.get('image_url', ''),
            stock_quantity=int(data.get('stock_quantity', 0))
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": product.to_dict(),
            "message": "Product created successfully"
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Invalid data format",
            "message": str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error creating product: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to create product",
            "message": str(e)
        }), 500

# Get all unique categories
@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all unique product categories"""
    try:
        categories = db.session.query(Product.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            "success": True,
            "data": category_list,
            "count": len(category_list)
        }), 200
        
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch categories",
            "message": str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "message": "The requested resource was not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500

# Initialize database with sample data
def init_sample_data():
    """Initialize database with sample products if empty"""
    try:
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
                ),
                Product(
                    name="Wireless Headphones",
                    description="Premium noise-cancelling wireless headphones",
                    price=199.99,
                    category="Electronics",
                    image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",
                    stock_quantity=12
                ),
                Product(
                    name="Yoga Mat",
                    description="Non-slip yoga mat for home workouts",
                    price=29.99,
                    category="Sports",
                    image_url="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=300",
                    stock_quantity=20
                )
            ]
            
            for product in sample_products:
                db.session.add(product)
            
            db.session.commit()
            print("✅ Sample data initialized successfully!")
            
    except Exception as e:
        print(f"❌ Error initializing sample data: {str(e)}")
        db.session.rollback()

# Application startup
if __name__ == '__main__':
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Initialize with sample data
            init_sample_data()
            
        except Exception as e:
            print(f"❌ Error during database initialization: {str(e)}")
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=True)