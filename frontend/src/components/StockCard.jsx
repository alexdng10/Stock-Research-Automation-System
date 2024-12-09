  import React, { useState, useEffect } from 'react';
  import { ChevronDown, ChevronUp } from 'lucide-react';
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

  // StockChart Component
  const StockChart = ({ stock }) => {
    // Only include historical dates (not future dates)
    const today = new Date();
    const validData = React.useMemo(() => {
      if (!stock?.historical_data?.dates || !stock?.historical_data?.prices) {
        return null;
      }

      const filteredData = stock.historical_data.dates.reduce((acc, date, index) => {
        const parsedDate = new Date(date);
        if (!isNaN(parsedDate) && parsedDate <= today) {
          acc.dates.push(parsedDate);
          acc.prices.push(stock.historical_data.prices[index]);
        }
        return acc;
      }, { dates: [], prices: [] });

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
      datasets: [{
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
      }]
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
            title: (items) => new Date(items[0].label).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            }),
            label: (context) => `$${context.parsed.y.toFixed(2)}`
          }
        }
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'month',
            displayFormats: { month: 'MMM yyyy' }
          },
          grid: { display: false },
          ticks: { color: '#888888', font: { size: 10 } }
        },
        y: {
          position: 'right',
          grid: { display: false },
          ticks: {
            color: '#888888',
            font: { size: 10 },
            callback: (value) => `$${value.toFixed(0)}`
          }
        }
      }
    };

    return (
      <div className="h-[120px] w-full mt-2">
        <Line data={chartData} options={options} />
      </div>
    );
  };

  // StockCard Component
  const StockCard = ({ stock }) => {
    const [expanded, setExpanded] = useState(false);
    const isPositive = stock.daily_change_percent > 0;
    const isNegative = stock.daily_change_percent < 0;

    const formatNumber = (num) => {
      if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
      if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
      if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
      if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
      return num.toFixed(2);
    };

    const renderMetricBadge = (metric, value) => {
      let colorClass = 'text-[#94a3b8] border-[#475569]/30 bg-[#475569]/10';
      if (value === 'strong' || value === 'high' || value === 'bullish') {
        colorClass = 'text-[#2ecc71] border-[#2ecc71]/30 bg-[#2ecc71]/10';
      }
      if (value === 'weak' || value === 'low' || value === 'bearish') {
        colorClass = 'text-[#e74c3c] border-[#e74c3c]/30 bg-[#e74c3c]/10';
      }
      
      return (
        <span className={`inline-flex items-center px-3 py-1 rounded-md border ${colorClass} text-xs backdrop-blur-md`}>
          {metric}: {value}
        </span>
      );
    };

    return (
      <div className="stock-card bg-[#1a1a1a]/50 border border-[#333333]/30 rounded-lg backdrop-blur-md">
        {/* Header */}
        <div className="flex justify-between items-start mb-6 p-4">
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-bold text-[#f1c40f]">{stock.symbol}</h3>
              <span className="text-[#94a3b8] text-sm">{stock.name}</span>
            </div>
            <div className="text-sm text-[#94a3b8] mt-1">
              {stock.sector} | {stock.industry}
            </div>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-[#94a3b8] hover:text-[#2ecc71] transition-colors p-1"
          >
            {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>

        {/* Price Information */}
        <div className="grid grid-cols-2 gap-6 mb-4 px-4">
          <div>
            <div className="text-2xl font-mono tracking-tight">
              ${stock.current_price.toFixed(2)}
            </div>
            <div className={`text-sm mt-1 ${isPositive ? 'text-[#2ecc71]' : isNegative ? 'text-[#e74c3c]' : 'text-[#94a3b8]'}`}>
              {isPositive ? '+' : ''}{stock.daily_change_percent.toFixed(2)}%
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-[#94a3b8]">Market Cap</div>
            <div className="text-lg font-mono tracking-tight mt-1">{stock.market_cap_formatted}</div>
          </div>
        </div>

        {/* Stock Chart */}
        <div className="px-4">
          <StockChart stock={stock} />
        </div>
        {/* Trading Information */}
        <div className="grid grid-cols-2 gap-6 text-sm mb-4 mt-4 px-4">
          <div>
            <div className="text-[#94a3b8]">Volume</div>
            <div className="font-mono mt-1">{formatNumber(stock.volume)}</div>
          </div>
          <div className="text-right">
            <div className="text-[#94a3b8]">Day Range</div>
            <div className="font-mono mt-1">${stock.day_low.toFixed(2)} - ${stock.day_high.toFixed(2)}</div>
          </div>
        </div>

        {/* Expanded Analysis */}
        {expanded && stock.analysis && (
          <div className="mt-4 border-t border-[#475569]/30 pt-6 px-4">
            <div className="flex flex-wrap gap-2 mb-6">
              {Object.entries(stock.analysis.key_metrics).map(([metric, value]) => (
                <div key={metric}>
                  {renderMetricBadge(
                    metric.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
                    value
                  )}
                </div>
              ))}
            </div>
            <div className="space-y-6">
              <div>
                <h4 className="text-[#f1c40f] mb-2 font-medium tracking-wide">Performance Summary</h4>
                <p className="text-sm text-[#94a3b8] leading-relaxed">{stock.analysis.performance_summary}</p>
              </div>
              <div>
                <h4 className="text-[#f1c40f] mb-2 font-medium tracking-wide">Trading Volume Analysis</h4>
                <p className="text-sm text-[#94a3b8] leading-relaxed">{stock.analysis.trading_volume_analysis}</p>
              </div>
              <div>
                <h4 className="text-[#f1c40f] mb-2 font-medium tracking-wide">Technical Signals</h4>
                <p className="text-sm text-[#94a3b8] leading-relaxed">{stock.analysis.technical_signals}</p>
              </div>
              <div>
                <h4 className="text-[#f1c40f] mb-2 font-medium tracking-wide">Market Sentiment</h4>
                <p className="text-sm text-[#94a3b8] leading-relaxed">{stock.analysis.market_sentiment}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  export default StockCard;