// InvGuard Frontend Configuration
const config = {
  // API Configuration
  API_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
  
  // Application Configuration
  APP_NAME: 'InvGuard',
  APP_VERSION: '1.0.0',
  
  // UI Configuration
  ITEMS_PER_PAGE: 20,
  MAX_TRANSACTION_QUANTITY: 10000,
  
  // Default Values
  DEFAULT_REORDER_LEVEL: 10,
  DEFAULT_CURRENCY: 'USD',
  
  // Chart Configuration
  CHART_COLORS: {
    primary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#06b6d4'
  }
};

export default config;
