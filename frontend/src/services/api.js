import axios from 'axios';

// API Base URL - no /api prefix since we're calling direct endpoints
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Clean the URL (remove any trailing slashes and /api suffixes)
const baseURL = API_BASE_URL.replace(/\/api$/, '').replace(/\/$/, '');

console.log('API Service Configuration:', {
  originalUrl: process.env.REACT_APP_API_URL,
  cleanedBaseUrl: baseURL,
  allEnvVars: {
    userPoolId: process.env.REACT_APP_USER_POOL_ID,
    userPoolClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID,
    identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID,
    apiUrl: process.env.REACT_APP_API_URL,
    region: process.env.REACT_APP_AWS_REGION
  }
});

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 15000, // 15 second timeout
});

// Add request interceptor for debugging and error handling
api.interceptors.request.use(
  (config) => {
    const fullUrl = `${config.baseURL}${config.url}`;
    console.log(`🔄 Making API request: ${config.method?.toUpperCase()} ${fullUrl}`);
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API response received from ${response.config.url}:`, {
      status: response.status,
      statusText: response.statusText,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('❌ API response error:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url
    });
    
    // Enhance error message for better debugging
    if (error.response) {
      // Server responded with error status
      error.message = `Server Error (${error.response.status}): ${error.response.statusText}`;
    } else if (error.request) {
      // Request was made but no response received
      error.message = 'Network Error: No response from server';
    }
    
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check endpoint
  async healthCheck() {
    try {
      console.log('🏥 Performing health check...');
      const response = await api.get('/health');
      console.log('✅ Health check successful:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Health check failed:', error.message);
      throw new Error(`Health check failed: ${error.message}`);
    }
  },

  // Get all products
  async getProducts() {
    try {
      console.log('📦 Fetching all products...');
      const response = await api.get('/products');
      console.log('✅ Products fetched successfully:', {
        count: response.data?.data?.length || 0,
        success: response.data?.success
      });
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching products:', error.message);
      throw new Error(`Failed to fetch products: ${error.message}`);
    }
  },

  // Get product by ID
  async getProduct(productId) {
    try {
      console.log(`📦 Fetching product ID: ${productId}...`);
      const response = await api.get(`/products/${productId}`);
      console.log('✅ Product fetched successfully:', response.data?.data?.name);
      return response.data;
    } catch (error) {
      console.error(`❌ Error fetching product ${productId}:`, error.message);
      throw new Error(`Failed to fetch product: ${error.message}`);
    }
  },

  // Get products by category
  async getProductsByCategory(category) {
    try {
      console.log(`🏷️ Fetching products in category: ${category}...`);
      const response = await api.get(`/products/category/${encodeURIComponent(category)}`);
      console.log('✅ Category products fetched successfully:', {
        category,
        count: response.data?.data?.length || 0
      });
      return response.data;
    } catch (error) {
      console.error(`❌ Error fetching products by category ${category}:`, error.message);
      throw new Error(`Failed to fetch products in category "${category}": ${error.message}`);
    }
  },

  // Get all categories
  async getCategories() {
    try {
      console.log('🏷️ Fetching categories...');
      const response = await api.get('/categories');
      console.log('✅ Categories fetched successfully:', {
        count: response.data?.data?.length || 0
      });
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching categories:', error.message);
      throw new Error(`Failed to fetch categories: ${error.message}`);
    }
  },

  // Create new product (admin function)
  async createProduct(productData) {
    try {
      console.log('➕ Creating new product:', productData.name);
      const response = await api.post('/products', productData);
      console.log('✅ Product created successfully:', response.data?.data?.name);
      return response.data;
    } catch (error) {
      console.error('❌ Error creating product:', error.message);
      throw new Error(`Failed to create product: ${error.message}`);
    }
  },

  // Test connectivity (useful for debugging)
  async testConnection() {
    try {
      console.log('🔍 Testing API connectivity...');
      const start = Date.now();
      await this.healthCheck();
      const duration = Date.now() - start;
      console.log(`✅ Connection test successful (${duration}ms)`);
      return { success: true, duration };
    } catch (error) {
      console.error('❌ Connection test failed:', error.message);
      return { success: false, error: error.message };
    }
  }
};

// Export default for backward compatibility
export default apiService;