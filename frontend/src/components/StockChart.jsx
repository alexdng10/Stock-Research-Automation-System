import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const StockChart = ({ data, isPositive }) => {
  // Default to sample data if no data provided
  const chartData = {
    labels: data?.labels || Array.from({ length: 20 }, (_, i) => i + 1),
    datasets: [
      {
        label: 'Price',
        data: data?.prices || Array.from({ length: 20 }, () => Math.random() * 100),
        borderColor: isPositive ? '#00ff00' : '#ff4444',
        backgroundColor: isPositive ? 'rgba(0, 255, 0, 0.1)' : 'rgba(255, 68, 68, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: '#1a1a1a',
        titleColor: '#ffd700',
        bodyColor: '#ffffff',
        borderColor: '#333333',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        display: false,
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
  };

  return (
    <div className="h-[100px] w-full mt-2">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default StockChart;
