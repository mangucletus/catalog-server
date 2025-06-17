from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Product
from config import Config

# Create Flask application instance
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object(Config)

# Enable CORS (Cross-Origin Resource Sharing) for frontend communication
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialize database with Flask app
db.init_app(app)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running"""
    return jsonify({'status': 'healthy', 'message': 'Catalog server is running'})

@app.route('/products', methods=['GET'])
def get_products():
    """Get all products from database"""
    try:
        # Query all products from database
        products = Product.query.all()
        
        # Convert products to dictionary format for JSON response
        products_list = [product.to_dict() for product in products]
        
        return jsonify({
            'success': True,
            'data': products_list,
            'count': len(products_list)
        })
    except Exception as e:
        # Return error if something goes wrong
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        # Find product by ID or return 404 if not found
        product = Product.query.get_or_404(product_id)
        
        return jsonify({
            'success': True,
            'data': product.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

@app.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('name') or not data.get('price'):
            return jsonify({
                'success': False,
                'error': 'Name and price are required'
            }), 400
        
        # Create new product instance
        new_product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            category=data.get('category', ''),
            stock_quantity=data.get('stock_quantity', 0),
            image_url=data.get('image_url', '')
        )
        
        # Add to database
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': new_product.to_dict(),
            'message': 'Product created successfully'
        }), 201
        
    except Exception as e:
        # Rollback database changes if error occurs
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    """Get products by category"""
    try:
        # Query products by category
        products = Product.query.filter_by(category=category).all()
        products_list = [product.to_dict() for product in products]
        
        return jsonify({
            'success': True,
            'data': products_list,
            'count': len(products_list),
            'category': category
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def create_sample_data():
    """Create sample products for testing"""
    sample_products = [
        {
            'name': 'Laptop Pro',
            'description': 'High-performance laptop for professionals',
            'price': 1299.99,
            'category': 'Electronics',
            'stock_quantity': 15,
            'image_url': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300'
        },
        {
            'name': 'Smartphone X',
            'description': 'Latest smartphone with amazing camera',
            'price': 899.99,
            'category': 'Electronics',
            'stock_quantity': 25,
            'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300'
        },
        {
            'name': 'Coffee Maker',
            'description': 'Automatic coffee maker for perfect brew',
            'price': 129.99,
            'category': 'Home',
            'stock_quantity': 8,
            'image_url': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=300'
        },
        {
            'name': 'Running Shoes',
            'description': 'Comfortable running shoes for daily exercise',
            'price': 89.99,
            'category': 'Sports',
            'stock_quantity': 30,
            'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300'
        }
    ]
    
    for product_data in sample_products:
        # Check if product already exists
        existing = Product.query.filter_by(name=product_data['name']).first()
        if not existing:
            product = Product(**product_data)
            db.session.add(product)
    
    db.session.commit()

if __name__ == '__main__':
    # Create database tables and sample data
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    # Run Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)