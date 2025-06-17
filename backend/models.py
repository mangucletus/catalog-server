from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy (database ORM)
db = SQLAlchemy()

class Product(db.Model):
    """Product model for storing catalog items in database"""
    
    # Table name in database
    __tablename__ = 'products'
    
    # Primary key - unique identifier for each product
    id = db.Column(db.Integer, primary_key=True)
    
    # Product name - required field
    name = db.Column(db.String(255), nullable=False)
    
    # Product description - optional field
    description = db.Column(db.Text, nullable=True)
    
    # Product price - required field, using Float for decimal numbers
    price = db.Column(db.Float, nullable=False)
    
    # Category for organizing products
    category = db.Column(db.String(100), nullable=True)
    
    # Stock quantity
    stock_quantity = db.Column(db.Integer, default=0)
    
    # Image URL for product picture
    image_url = db.Column(db.String(500), nullable=True)
    
    def to_dict(self):
        """Convert product object to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url
        }
    
    def __repr__(self):
        """String representation of Product object"""
        return f'<Product {self.name}>'