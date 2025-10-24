import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AnalyticsCharts from '../components/AnalyticsCharts';
import { toast } from 'react-hot-toast';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function Analytics() {
  const [loading, setLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState({
    lowStockItems: [],
    categorySummary: [],
    stockTrends: [],
    topItems: [],
    dashboardStats: null
  });
  const [viewMode, setViewMode] = useState('overview'); // overview, inventory, trends

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const [
        lowStockResponse,
        categoryResponse,
        trendsResponse,
        topItemsResponse,
        dashboardResponse
      ] = await Promise.all([
        axios.get(`${API_URL}/analytics/low-stock`, { headers }),
        axios.get(`${API_URL}/analytics/category-summary`, { headers }),
        axios.get(`${API_URL}/analytics/stock-trends`, { headers }),
        axios.get(`${API_URL}/analytics/top-items`, { headers }),
        axios.get(`${API_URL}/analytics/dashboard`, { headers })
      ]);

      setAnalyticsData({
        lowStockItems: lowStockResponse.data,
        categorySummary: categoryResponse.data,
        stockTrends: trendsResponse.data,
        topItems: topItemsResponse.data,
        dashboardStats: dashboardResponse.data
      });
    } catch (error) {
      console.error('Error fetching analytics data:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
              <div className="h-12 w-12 bg-gray-200 rounded-xl mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-16"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Analytics</h1>
          <p className="text-gray-600 mt-1">Comprehensive insights and performance metrics</p>
        </div>
        <div className="flex items-center space-x-3">
          {/* View Mode Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('overview')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                viewMode === 'overview'
                  ? 'bg-white shadow text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setViewMode('inventory')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                viewMode === 'inventory'
                  ? 'bg-white shadow text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Inventory
            </button>
            <button
              onClick={() => setViewMode('trends')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                viewMode === 'trends'
                  ? 'bg-white shadow text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Trends
            </button>
          </div>

          <button
            onClick={fetchAnalyticsData}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition transform hover:scale-105"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-white/20 rounded-xl">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <div className="text-right">
              <p className="text-blue-100 text-sm font-medium">Total Items</p>
              <p className="text-3xl font-bold">
                {analyticsData.dashboardStats?.total_items || 0}
              </p>
            </div>
          </div>
          <div className="h-1 bg-white/30 rounded-full overflow-hidden">
            <div className="h-full bg-white/60 rounded-full" style={{ width: '85%' }}></div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-white/20 rounded-xl">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
            </div>
            <div className="text-right">
              <p className="text-green-100 text-sm font-medium">Categories</p>
              <p className="text-3xl font-bold">
                {analyticsData.dashboardStats?.total_categories || 0}
              </p>
            </div>
          </div>
          <div className="h-1 bg-white/30 rounded-full overflow-hidden">
            <div className="h-full bg-white/60 rounded-full" style={{ width: '70%' }}></div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-white/20 rounded-xl">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="text-right">
              <p className="text-purple-100 text-sm font-medium">Total Value</p>
              <p className="text-3xl font-bold">
                ${analyticsData.dashboardStats?.total_inventory_value?.toFixed(2) || '0.00'}
              </p>
            </div>
          </div>
          <div className="h-1 bg-white/30 rounded-full overflow-hidden">
            <div className="h-full bg-white/60 rounded-full" style={{ width: '92%' }}></div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition animate-pulse-slow">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-white/20 rounded-xl">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="text-right">
              <p className="text-red-100 text-sm font-medium">Low Stock Alerts</p>
              <p className="text-3xl font-bold">
                {analyticsData.dashboardStats?.low_stock_alerts || 0}
              </p>
            </div>
          </div>
          <div className="h-1 bg-white/30 rounded-full overflow-hidden">
            <div className="h-full bg-white/60 rounded-full animate-pulse" style={{ width: '45%' }}></div>
          </div>
        </div>
      </div>

      {/* Low Stock Alerts */}
      {viewMode === 'overview' && analyticsData.lowStockItems.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border-l-4 border-red-500">
          <div className="p-6 bg-gradient-to-r from-red-50 to-orange-50">
            <div className="flex items-center">
              <div className="p-3 bg-red-100 rounded-xl">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="ml-4">
                <h2 className="text-xl font-bold text-gray-800">⚠️ Low Stock Alerts</h2>
                <p className="text-sm text-gray-600">Items that need immediate attention</p>
              </div>
              <div className="ml-auto">
                <span className="px-4 py-2 bg-red-500 text-white rounded-full text-sm font-bold">
                  {analyticsData.lowStockItems.length} items
                </span>
              </div>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Item</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">SKU</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Current Stock</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Reorder Level</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Shortage</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {analyticsData.lowStockItems.map((item) => {
                  const urgency = item.shortage / item.reorder_level;
                  return (
                    <tr key={item.id} className="hover:bg-red-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">{item.name}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded text-gray-700">
                          {item.sku}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-blue-100 text-blue-700 text-xs font-medium">
                          {item.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <span className="inline-flex items-center px-3 py-1 rounded-lg text-sm font-bold bg-red-100 text-red-800 animate-pulse">
                            {item.current_stock}
                          </span>
                          <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                          </svg>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">{item.reorder_level}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-3 py-1 rounded-lg text-sm font-bold bg-orange-100 text-orange-800">
                          -{item.shortage}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                          urgency > 0.8 ? 'bg-red-100 text-red-800' :
                          urgency > 0.5 ? 'bg-orange-100 text-orange-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {urgency > 0.8 ? '🔴 Critical' : urgency > 0.5 ? '🟠 High' : '🟡 Medium'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Charts Section */}
      {(viewMode === 'overview' || viewMode === 'trends') && (
        <div className="space-y-6">
          <AnalyticsCharts 
            categorySummary={analyticsData.categorySummary}
            stockTrends={analyticsData.stockTrends}
          />
        </div>
      )}

      {/* Top Items by Value */}
      {(viewMode === 'overview' || viewMode === 'inventory') && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-purple-50 to-indigo-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="p-3 bg-purple-100 rounded-xl">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <div className="ml-4">
                  <h2 className="text-xl font-bold text-gray-800">Top Items by Value</h2>
                  <p className="text-sm text-gray-600">Highest value inventory items</p>
                </div>
              </div>
              <span className="px-3 py-1 bg-purple-100 text-purple-600 rounded-full text-sm font-medium">
                Top {analyticsData.topItems.length}
              </span>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Item</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Quantity</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Unit Price</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Total Value</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">% of Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {analyticsData.topItems.map((item, index) => {
                  const percentage = (item.total_value / analyticsData.dashboardStats?.total_inventory_value * 100).toFixed(1);
                  return (
                    <tr key={item.id} className="hover:bg-purple-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {index < 3 && (
                            <span className="text-2xl mr-2">
                              {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                            </span>
                          )}
                          <span className="text-sm font-bold text-gray-900">#{index + 1}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">{item.name}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-blue-100 text-blue-700 text-xs font-medium">
                          {item.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-semibold text-gray-900">{item.quantity}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">${item.price.toFixed(2)}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-bold text-green-600">${item.total_value.toFixed(2)}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 w-20">
                            <div 
                              className="bg-gradient-to-r from-purple-500 to-indigo-600 h-2 rounded-full" 
                              style={{ width: `${Math.min(percentage, 100)}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-700">{percentage}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {analyticsData.topItems.length === 0 && (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p className="mt-2 text-sm text-gray-500">No items found</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Category Breakdown */}
      {(viewMode === 'overview' || viewMode === 'inventory') && analyticsData.categorySummary.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center mb-6">
            <div className="p-3 bg-indigo-100 rounded-xl">
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
            </div>
            <div className="ml-4">
              <h2 className="text-xl font-bold text-gray-800">Category Breakdown</h2>
              <p className="text-sm text-gray-600">Distribution across categories</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analyticsData.categorySummary.map((category, index) => {
              const colors = [
                'from-blue-500 to-blue-600',
                'from-green-500 to-green-600',
                'from-purple-500 to-purple-600',
                'from-orange-500 to-orange-600',
                'from-pink-500 to-pink-600',
                'from-indigo-500 to-indigo-600'
              ];
              const color = colors[index % colors.length];

              return (
                <div 
                  key={category.category}
                  className={`bg-gradient-to-br ${color} rounded-xl p-6 text-white transform hover:scale-105 transition shadow-lg`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-bold">{category.category}</h3>
                    <svg className="w-6 h-6 opacity-75" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-white/80 text-sm">Items:</span>
                      <span className="text-xl font-bold">{category.total_items}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-white/80 text-sm">Value:</span>
                      <span className="text-xl font-bold">${category.total_value.toFixed(2)}</span>
                    </div>
                    <div className="h-2 bg-white/30 rounded-full overflow-hidden mt-3">
                      <div 
                        className="h-full bg-white/60 rounded-full" 
                        style={{ 
                          width: `${(category.total_value / analyticsData.dashboardStats?.total_inventory_value * 100).toFixed(0)}%` 
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Quick Insights */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
        <div className="flex items-start">
          <div className="ml-4 flex-1">
            <h3 className="text-lg font-bold text-gray-800 mb-3">💡 Quick Insights</h3>
            <div className="space-y-2">
              {analyticsData.lowStockItems.length > 0 && (
                <div className="flex items-start space-x-2">
                  <span className="text-red-500 mt-1">•</span>
                  <p className="text-gray-700">
                    <strong>{analyticsData.lowStockItems.length}</strong> items need reordering to maintain optimal stock levels
                  </p>
                </div>
              )}
              {analyticsData.topItems.length > 0 && (
                <div className="flex items-start space-x-2">
                  <span className="text-green-500 mt-1">•</span>
                  <p className="text-gray-700">
                    Top 3 items account for <strong>${analyticsData.topItems.slice(0, 3).reduce((sum, item) => sum + item.total_value, 0).toFixed(2)}</strong> in total value
                  </p>
                </div>
              )}
              {analyticsData.categorySummary.length > 0 && (
                <div className="flex items-start space-x-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <p className="text-gray-700">
                    <strong>{analyticsData.categorySummary[0]?.category}</strong> is your largest category with {analyticsData.categorySummary[0]?.total_items} items
                  </p>
                </div>
              )}
              <div className="flex items-start space-x-2">
                <span className="text-purple-500 mt-1">•</span>
                <p className="text-gray-700">
                  Total inventory value: <strong>${analyticsData.dashboardStats?.total_inventory_value?.toFixed(2) || '0.00'}</strong>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;