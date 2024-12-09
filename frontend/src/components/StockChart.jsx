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
  Filler,
  TimeScale,
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Register ChartJS components
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

const StockChart = ({ data, isPositive }) => {
  const lineColor = isPositive ? '#2ecc71' : '#e74c3c';
  const gradientColor = isPositive ? 'rgba(46, 204, 113, 0.1)' : 'rgba(231, 76, 60, 0.1)';

  if (!data?.labels || !data?.prices || data.labels.length === 0 || data.prices.length === 0) {
    return (
      <div className="h-[120px] w-full mt-2 flex items-center justify-center text-[#888888] text-sm">
        No historical data available
      </div>
    );
  }

  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Price',
        data: data.prices,
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
        pointHoverBackgroundColor: lineColor,
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2,
        borderWidth: 1.5,
        cubicInterpolationMode: 'monotone',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 750,
      easing: 'easeInOutQuart'
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#f1c40f',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(71, 85, 105, 0.3)',
        borderWidth: 1,
        padding: 10,
        bodyFont: {
          family: "'JetBrains Mono', monospace",
          size: 12,
        },
        titleFont: {
          family: "'JetBrains Mono', monospace",
          size: 12,
          weight: 'bold',
        },
        displayColors: false,
        callbacks: {
          title: function(tooltipItems) {
            const date = new Date(tooltipItems[0].label);
            return date.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            });
          },
          label: function(context) {
            return `$${context.parsed.y.toFixed(2)}`;
          }
        }
      },
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'month',
          displayFormats: {
            month: 'MMM yyyy'
          }
        },
        display: false,
        grid: {
          display: false,
        },
      },
      y: {
        display: false,
        grid: {
          display: false,
        },
      },
    },
    interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false,
    },
    elements: {
      line: {
        borderCapStyle: 'round',
        borderJoinStyle: 'round',
      },
      point: {
        hitRadius: 10,
      }
    },
  };

  return (
    <div className="h-[120px] w-full mt-2 chart-container">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default StockChart;
