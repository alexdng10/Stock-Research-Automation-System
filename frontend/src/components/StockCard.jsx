import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import StockChart from './StockChart';

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
    <div className="stock-card">
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
        <StockChart isPositive={isPositive} data={stock.historical_data} />
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
          {/* Key Metrics */}
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

          {/* Analysis Sections */}
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
