import React, { useState, useEffect } from 'react';
import ProductCard from '../components/ProductCard';
import { apiService } from '../services/api';
import './HomePage.css';

const HomePage = ({ user, signOut }) => {
  // State for storing products and loading status
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Fetch products when component mounts
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await apiService.getProducts();
      
      if (response.success) {
        setProducts(response.data);
      } else {
        setError('Failed to fetch products');
      }
    } catch (err) {
      setError('Error connecting to server. Please try again later.');
      console.error('Error fetching products:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter products by category
  const filterProductsByCategory = async (category) => {
    try {
      setLoading(true);
      setSelectedCategory(category);
      
      if (category === 'all') {
        const response = await apiService.getProducts();
        if (response.success) {
          setProducts(response.data);
        }
      } else {
        const response = await apiService.getProductsByCategory(category);
        if (response.success) {
          setProducts(response.data);
        }
      }
    } catch (err) {
      setError('Error filtering products');
      console.error('Error filtering products:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get unique categories from products
  const getCategories = () => {
    const categories = products.map(product => product.category);
    return [...new Set(categories)].filter(Boolean);
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading products...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={fetchProducts} className="retry-btn">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="home-page">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>Product Catalog</h1>
          <div className="user-info">
            <span>Welcome, {user?.username || 'User'}!</span>
            <button onClick={signOut} className="sign-out-btn">
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Category Filter */}
      <div className="category-filter">
        <button 
          className={`category-btn ${selectedCategory === 'all' ? 'active' : ''}`}
          onClick={() => filterProductsByCategory('all')}
        >
          All Products
        </button>
        {getCategories().map(category => (
          <button 
            key={category}
            className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
            onClick={() => filterProductsByCategory(category)}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Products Grid */}
      <main className="main-content">
        {products.length === 0 ? (
          <div className="no-products">
            <h2>No products found</h2>
            <p>There are no products available at the moment.</p>
          </div>
        ) : (
          <div className="products-grid">
            {products.map(product => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default HomePage;