import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-date-fns';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
);

const StockChart = ({ stock }) => {
  const today = new Date();

  // Filter and validate data
  const validData = React.useMemo(() => {
    if (!stock?.historical_data?.dates || !stock?.historical_data?.prices) {
      return null;
    }

    const filteredData = stock.historical_data.dates.reduce(
      (acc, date, index) => {
        const parsedDate = new Date(date);
        if (!isNaN(parsedDate) && parsedDate <= today) {
          acc.dates.push(parsedDate);
          acc.prices.push(stock.historical_data.prices[index]);
        }
        return acc;
      },
      { dates: [], prices: [] }
    );

    return filteredData.dates.length > 0 ? filteredData : null;
  }, [stock?.historical_data, today]);

  if (!validData) {
    return (
      <div className="h-[120px] w-full mt-2 flex items-center justify-center text-[#888888] text-sm">
        No historical data available
      </div>
    );
  }

  const isPositive = stock.daily_change_percent > 0;
  const lineColor = isPositive ? '#2ecc71' : '#e74c3c';
  const gradientColor = isPositive ? 'rgba(46, 204, 113, 0.1)' : 'rgba(231, 76, 60, 0.1)';

  const chartData = {
    labels: validData.dates,
    datasets: [
      {
        label: 'Price',
        data: validData.prices,
        borderColor: lineColor,
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 100);
          gradient.addColorStop(0, gradientColor);
          gradient.addColorStop(1, 'rgba(15, 23, 42, 0)');
          return gradient;
        },
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 1.5,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f1c40f',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(71, 85, 105, 0.3)',
        borderWidth: 1,
        padding: 10,
        displayColors: false,
        callbacks: {
          title: (items) =>
            new Date(items[0].label).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            }),
          label: (context) => `$${context.parsed.y.toFixed(2)}`,
        },
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'month',
          displayFormats: { month: 'MMM yyyy' },
        },
        grid: { display: false },
        ticks: { color: '#888888', font: { size: 10 } },
      },
      y: {
        position: 'right',
        grid: { display: false },
        ticks: {
          color: '#888888',
          font: { size: 10 },
          callback: (value) => `$${value.toFixed(0)}`,
        },
      },
    },
  };

  return (
    <div className="h-[120px] w-full mt-2">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default StockChart;
