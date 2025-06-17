import React from 'react';
import './ProductCard.css';

const ProductCard = ({ product }) => {
  // Format price to display with currency
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  return (
    <div className="product-card">
      {/* Product Image */}
      <div className="product-image">
        <img 
          src={product.image_url || '/placeholder-image.jpg'} 
          alt={product.name}
          onError={(e) => {
            // Fallback image if main image fails to load
            e.target.src = 'https://via.placeholder.com/300x200?text=No+Image';
          }}
        />
      </div>
      
      {/* Product Info */}
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-description">{product.description}</p>
        
        <div className="product-details">
          <span className="product-price">{formatPrice(product.price)}</span>
          <span className="product-category">{product.category}</span>
        </div>
        
        <div className="product-stock">
          <span className={`stock-status ${product.stock_quantity > 0 ? 'in-stock' : 'out-of-stock'}`}>
            {product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'Out of stock'}
          </span>
        </div>
        
        <button 
          className={`add-to-cart-btn ${product.stock_quantity === 0 ? 'disabled' : ''}`}
          disabled={product.stock_quantity === 0}
        >
          {product.stock_quantity > 0 ? 'Add to Cart' : 'Out of Stock'}
        </button>
      </div>
    </div>
  );
};

export default ProductCard;