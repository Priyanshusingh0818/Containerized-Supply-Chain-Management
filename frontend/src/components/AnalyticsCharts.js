import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

function AnalyticsCharts({ categorySummary, stockTrends }) {
  const categoryChartData = {
    labels: categorySummary.map(item => item.category),
    datasets: [
      {
        label: 'Total Items',
        data: categorySummary.map(item => item.total_items),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      },
      {
        label: 'Total Value ($)',
        data: categorySummary.map(item => item.total_value),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }
    ]
  };

  const trendsChartData = {
    labels: stockTrends.map(item => item.date),
    datasets: [
      {
        label: 'Stock In',
        data: stockTrends.map(item => item.stock_in),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.3
      },
      {
        label: 'Stock Out',
        data: stockTrends.map(item => item.stock_out),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.3
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top'
      }
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">Category Summary</h3>
        <Bar data={categoryChartData} options={chartOptions} />
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">Stock Trends (Last 30 Days)</h3>
        <Line data={trendsChartData} options={chartOptions} />
      </div>
    </div>
  );
}

export default AnalyticsCharts;