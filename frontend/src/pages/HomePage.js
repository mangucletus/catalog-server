import React, { useState, useEffect } from 'react';
import ProductCard from '../components/ProductCard';
import { apiService } from '../services/api';
import './HomePage.css';

const HomePage = ({ user, signOut }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [categories, setCategories] = useState([]);

  // Debug user information
  console.log('HomePage - User info:', {
    user,
    username: user?.username,
    email: user?.attributes?.email,
    signedIn: !!user
  });

  // Fetch products when component mounts
  useEffect(() => {
    console.log('HomePage mounted, fetching products...');
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      console.log('Fetching products...');
      setLoading(true);
      setError(null);
      
      // First test the health endpoint
      console.log('Testing health endpoint...');
      await apiService.healthCheck();
      console.log('Health check passed');
      
      // Then fetch products
      console.log('Fetching products from API...');
      const response = await apiService.getProducts();
      console.log('Products response:', response);
      
      if (response && response.success) {
        const productsData = response.data || [];
        setProducts(productsData);
        
        // Extract unique categories
        const uniqueCategories = [...new Set(productsData.map(product => product.category))].filter(Boolean);
        setCategories(uniqueCategories);
        
        console.log('Products loaded:', productsData.length);
        console.log('Categories found:', uniqueCategories);
      } else {
        setError('Failed to fetch products: Invalid response format');
        console.error('Invalid response format:', response);
      }
    } catch (err) {
      console.error('Error in fetchProducts:', err);
      
      // Provide more detailed error information
      let errorMessage = 'Error connecting to server';
      if (err.response) {
        errorMessage = `Server error: ${err.response.status} - ${err.response.statusText}`;
      } else if (err.request) {
        errorMessage = 'Network error: Unable to reach server';
      } else {
        errorMessage = `Request error: ${err.message}`;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Filter products by category
  const filterProductsByCategory = async (category) => {
    try {
      setLoading(true);
      setError(null);
      setSelectedCategory(category);
      
      console.log('Filtering by category:', category);
      
      if (category === 'all') {
        const response = await apiService.getProducts();
        if (response && response.success) {
          setProducts(response.data || []);
        }
      } else {
        const response = await apiService.getProductsByCategory(category);
        if (response && response.success) {
          setProducts(response.data || []);
        }
      }
    } catch (err) {
      console.error('Error filtering products:', err);
      setError(`Error filtering products: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Get user display name
  const getUserDisplayName = () => {
    if (!user) return 'Guest';
    return user.username || user.attributes?.email || user.attributes?.preferred_username || 'User';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading products...</p>
        <small>Connecting to server at {process.env.REACT_APP_API_URL || 'localhost:5000'}</small>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>Connection Error</h2>
        <p>{error}</p>
        <button onClick={fetchProducts} className="retry-btn">
          Try Again
        </button>
        <div className="debug-info">
          <p><strong>API URL:</strong> {process.env.REACT_APP_API_URL || 'http://localhost:5000'}</p>
          <p><strong>User Pool ID:</strong> {process.env.REACT_APP_USER_POOL_ID || 'Not set'}</p>
          <p><strong>AWS Region:</strong> {process.env.REACT_APP_AWS_REGION || 'Not set'}</p>
          <p><strong>User:</strong> {getUserDisplayName()}</p>
        </div>
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
            <span>Welcome, {getUserDisplayName()}!</span>
            <button onClick={signOut} className="sign-out-btn">
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Category Filter */}
      {categories.length > 0 && (
        <div className="category-filter">
          <button 
            className={`category-btn ${selectedCategory === 'all' ? 'active' : ''}`}
            onClick={() => filterProductsByCategory('all')}
          >
            All Products ({products.length})
          </button>
          {categories.map(category => (
            <button 
              key={category}
              className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
              onClick={() => filterProductsByCategory(category)}
            >
              {category}
            </button>
          ))}
        </div>
      )}

      {/* Products Grid */}
      <main className="main-content">
        {products.length === 0 ? (
          <div className="no-products">
            <h2>No products found</h2>
            <p>
              {selectedCategory === 'all' 
                ? "There are no products available at the moment." 
                : `No products found in the "${selectedCategory}" category.`
              }
            </p>
            <button onClick={fetchProducts} className="retry-btn">
              Refresh Products
            </button>
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