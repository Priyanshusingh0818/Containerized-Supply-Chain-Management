import React from 'react';

// Skeleton loader for table rows
export const TableSkeleton = ({ rows = 5, columns = 6 }) => (
  <div className="animate-pulse">
    {[...Array(rows)].map((_, rowIndex) => (
      <div key={rowIndex} className="flex items-center space-x-4 p-4 border-b border-gray-200">
        {[...Array(columns)].map((_, colIndex) => (
          <div key={colIndex} className="flex-1">
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
        ))}
      </div>
    ))}
  </div>
);

// Skeleton loader for stat cards
export const StatCardSkeleton = ({ count = 4 }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
    {[...Array(count)].map((_, i) => (
      <div key={i} className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
        <div className="flex items-center justify-between mb-4">
          <div className="h-12 w-12 bg-gray-200 rounded-xl"></div>
          <div className="h-2 w-2 bg-gray-200 rounded-full"></div>
        </div>
        <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
        <div className="h-8 bg-gray-200 rounded w-16"></div>
      </div>
    ))}
  </div>
);

// Skeleton loader for charts
export const ChartSkeleton = () => (
  <div className="bg-white p-6 rounded-2xl shadow-lg animate-pulse">
    <div className="h-6 bg-gray-200 rounded w-32 mb-6"></div>
    <div className="space-y-3">
      <div className="h-32 bg-gray-200 rounded"></div>
      <div className="h-24 bg-gray-200 rounded"></div>
      <div className="h-40 bg-gray-200 rounded"></div>
    </div>
  </div>
);

// Full page loading spinner
export const PageLoader = ({ message = 'Loading...' }) => (
  <div className="flex flex-col items-center justify-center h-64 space-y-4">
    <div className="relative">
      <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
      <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-purple-600 rounded-full animate-spin animation-delay-150"></div>
    </div>
    <p className="text-gray-600 font-medium">{message}</p>
  </div>
);

// Inline spinner
export const Spinner = ({ size = 'md', color = 'blue' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  const colors = {
    blue: 'border-blue-600',
    green: 'border-green-600',
    red: 'border-red-600',
    purple: 'border-purple-600'
  };

  return (
    <div className={`${sizes[size]} border-4 border-gray-200 ${colors[color]} border-t-transparent rounded-full animate-spin`}></div>
  );
};

// Card skeleton
export const CardSkeleton = () => (
  <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
    <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
    <div className="space-y-3">
      <div className="h-4 bg-gray-200 rounded"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      <div className="h-4 bg-gray-200 rounded w-4/6"></div>
    </div>
  </div>
);

export default {
  TableSkeleton,
  StatCardSkeleton,
  ChartSkeleton,
  PageLoader,
  Spinner,
  CardSkeleton
};