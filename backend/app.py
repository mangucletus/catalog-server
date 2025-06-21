from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv
from datetime import datetime

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'image_url': self.image_url,
            'stock_quantity': self.stock_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        product_count = Product.query.count()
        return jsonify({
            "status": "healthy",
            "message": "Catalog server is running",
            "database": "connected",
            "products_count": product_count,
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": "Database connection failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503

# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        # Get query parameters for potential filtering
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)
        
        query = Product.query
        
        if category:
            query = query.filter_by(category=category)
        
        # Order by creation date (newest first)
        query = query.order_by(Product.created_at.desc())
        
        if limit:
            query = query.limit(limit)
            
        products = query.all()
        products_data = [product.to_dict() for product in products]
        
        return jsonify({
            "success": True,
            "data": products_data,
            "count": len(products_data),
            "total_products": Product.query.count()
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

# Get products by category
@app.route('/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    """Get products filtered by category"""
    try:
        products = Product.query.filter_by(category=category).order_by(Product.created_at.desc()).all()
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
    """Create a new product"""
    try:
        data = request.get_json()
        
        # Enhanced validation
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
            
        # Check required fields
        required_fields = ['name', 'price']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Validate price
        try:
            price = float(data['price'])
            if price < 0:
                return jsonify({
                    "success": False,
                    "error": "Price cannot be negative"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Invalid price format"
            }), 400
        
        # Validate stock quantity
        stock_quantity = 0
        if 'stock_quantity' in data:
            try:
                stock_quantity = int(data['stock_quantity'])
                if stock_quantity < 0:
                    return jsonify({
                        "success": False,
                        "error": "Stock quantity cannot be negative"
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "error": "Invalid stock quantity format"
                }), 400
        
        # Create new product
        product = Product(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            price=price,
            category=data.get('category', 'Uncategorized').strip(),
            image_url=data.get('image_url', '').strip(),
            stock_quantity=stock_quantity
        )
        
        db.session.add(product)
        db.session.commit()
        
        print(f"✅ Product created successfully: {product.name} (ID: {product.id})")
        
        return jsonify({
            "success": True,
            "data": product.to_dict(),
            "message": "Product created successfully"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating product: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to create product",
            "message": str(e)
        }), 500

# Update product (bonus endpoint)
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                "success": False,
                "error": "Product not found"
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Update fields if provided
        if 'name' in data:
            product.name = data['name'].strip()
        if 'description' in data:
            product.description = data['description'].strip()
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({
                        "success": False,
                        "error": "Price cannot be negative"
                    }), 400
                product.price = price
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "error": "Invalid price format"
                }), 400
        if 'category' in data:
            product.category = data['category'].strip()
        if 'image_url' in data:
            product.image_url = data['image_url'].strip()
        if 'stock_quantity' in data:
            try:
                stock_quantity = int(data['stock_quantity'])
                if stock_quantity < 0:
                    return jsonify({
                        "success": False,
                        "error": "Stock quantity cannot be negative"
                    }), 400
                product.stock_quantity = stock_quantity
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "error": "Invalid stock quantity format"
                }), 400
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": product.to_dict(),
            "message": "Product updated successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating product {product_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to update product",
            "message": str(e)
        }), 500

# Delete product (bonus endpoint)
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({
                "success": False,
                "error": "Product not found"
            }), 404
        
        product_name = product.name
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Product '{product_name}' deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting product {product_id}: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to delete product",
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
            "data": sorted(category_list),
            "count": len(category_list)
        }), 200
        
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch categories",
            "message": str(e)
        }), 500

# Get statistics endpoint (bonus)
@app.route('/stats', methods=['GET'])
def get_stats():
    """Get catalog statistics"""
    try:
        total_products = Product.query.count()
        total_categories = db.session.query(Product.category).distinct().count()
        total_stock = db.session.query(db.func.sum(Product.stock_quantity)).scalar() or 0
        avg_price = db.session.query(db.func.avg(Product.price)).scalar() or 0
        
        # Products by category
        category_stats = db.session.query(
            Product.category,
            db.func.count(Product.id).label('count')
        ).group_by(Product.category).all()
        
        category_breakdown = {cat: count for cat, count in category_stats}
        
        return jsonify({
            "success": True,
            "data": {
                "total_products": total_products,
                "total_categories": total_categories,
                "total_stock": int(total_stock),
                "average_price": round(float(avg_price), 2),
                "category_breakdown": category_breakdown
            }
        }), 200
        
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch statistics",
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

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": "Bad request",
        "message": "The request was invalid"
    }), 400

# Initialize database with comprehensive sample data
def init_sample_data():
    """Initialize database with comprehensive sample products if empty"""
    try:
        if Product.query.count() == 0:
            print("🔄 Initializing database with sample data...")
            
            sample_products = [
                # Electronics
                Product(
                    name="MacBook Pro 16-inch",
                    description="Apple MacBook Pro with M3 Pro chip, 18GB RAM, 512GB SSD. Perfect for professionals and developers.",
                    price=2499.99,
                    category="Electronics",
                    image_url="https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=300&fit=crop",
                    stock_quantity=15
                ),
                Product(
                    name="iPhone 15 Pro",
                    description="Latest iPhone with A17 Pro chip, titanium design, and pro camera system.",
                    price=999.99,
                    category="Electronics",
                    image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop",
                    stock_quantity=25
                ),
                Product(
                    name="Sony WH-1000XM5",
                    description="Industry-leading noise canceling headphones with exceptional sound quality.",
                    price=399.99,
                    category="Electronics",
                    image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=300&fit=crop",
                    stock_quantity=12
                ),
                Product(
                    name="iPad Air 5th Gen",
                    description="Powerful iPad with M1 chip, 10.9-inch display, perfect for creativity and productivity.",
                    price=599.99,
                    category="Electronics",
                    image_url="https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=300&fit=crop",
                    stock_quantity=18
                ),
                Product(
                    name="Gaming Mechanical Keyboard",
                    description="RGB backlit mechanical keyboard with Cherry MX switches, perfect for gaming.",
                    price=149.99,
                    category="Electronics",
                    image_url="https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400&h=300&fit=crop",
                    stock_quantity=32
                ),
                
                # Home & Kitchen
                Product(
                    name="Breville Espresso Machine",
                    description="Professional-grade espresso machine with integrated grinder and milk frother.",
                    price=699.99,
                    category="Home",
                    image_url="https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=300&fit=crop",
                    stock_quantity=8
                ),
                Product(
                    name="Vitamix High-Speed Blender",
                    description="Professional-grade blender perfect for smoothies, soups, and food preparation.",
                    price=449.99,
                    category="Home",
                    image_url="https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400&h=300&fit=crop",
                    stock_quantity=5
                ),
                Product(
                    name="Smart LED Light Bulbs (4-Pack)",
                    description="WiFi-enabled smart bulbs with 16 million colors and voice control compatibility.",
                    price=79.99,
                    category="Home",
                    image_url="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop",
                    stock_quantity=24
                ),
                Product(
                    name="Robot Vacuum Cleaner",
                    description="Smart robot vacuum with mapping technology and app control.",
                    price=299.99,
                    category="Home",
                    image_url="https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400&h=300&fit=crop",
                    stock_quantity=10
                ),
                
                # Sports & Fitness
                Product(
                    name="Nike Air Zoom Pegasus 40",
                    description="Comfortable running shoes with responsive cushioning for daily training.",
                    price=129.99,
                    category="Sports",
                    image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=300&fit=crop",
                    stock_quantity=30
                ),
                Product(
                    name="Premium Yoga Mat",
                    description="Non-slip yoga mat made from eco-friendly materials, perfect for all yoga styles.",
                    price=59.99,
                    category="Sports",
                    image_url="https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=300&fit=crop",
                    stock_quantity=20
                ),
                Product(
                    name="Adjustable Dumbbells Set",
                    description="Space-saving adjustable dumbbells with weight range from 5-50 lbs each.",
                    price=299.99,
                    category="Sports",
                    image_url="https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&h=300&fit=crop",
                    stock_quantity=6
                ),
                Product(
                    name="Fitness Tracker Watch",
                    description="Advanced fitness tracker with heart rate monitoring, GPS, and 7-day battery life.",
                    price=249.99,
                    category="Sports",
                    image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=300&fit=crop",
                    stock_quantity=14
                ),
                
                # Books & Education
                Product(
                    name="Complete Python Programming Course",
                    description="Comprehensive online course with lifetime access and certificate of completion.",
                    price=89.99,
                    category="Education",
                    image_url="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=300&fit=crop",
                    stock_quantity=100
                ),
                Product(
                    name="Professional Photography Book Set",
                    description="3-book collection covering composition, lighting, and post-processing techniques.",
                    price=79.99,
                    category="Books",
                    image_url="https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=300&fit=crop",
                    stock_quantity=22
                ),
                
                # Clothing & Fashion
                Product(
                    name="Sustainable Cotton T-Shirt",
                    description="Organic cotton t-shirt made from sustainable materials, available in multiple colors.",
                    price=29.99,
                    category="Clothing",
                    image_url="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=300&fit=crop",
                    stock_quantity=45
                ),
                Product(
                    name="Premium Leather Backpack",
                    description="Handcrafted leather backpack with laptop compartment and lifetime warranty.",
                    price=199.99,
                    category="Clothing",
                    image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=300&fit=crop",
                    stock_quantity=12
                )
            ]
            
            for product in sample_products:
                db.session.add(product)
            
            db.session.commit()
            print(f"✅ {len(sample_products)} sample products initialized successfully!")
            
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
            
            # Print startup info
            product_count = Product.query.count()
            category_count = db.session.query(Product.category).distinct().count()
            print(f"📊 Database ready: {product_count} products across {category_count} categories")
            
        except Exception as e:
            print(f"❌ Error during database initialization: {str(e)}")
    
    # Run the application
    print("🚀 Starting Catalog Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)