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
    let color = 'text-[#666666]';
    if (value === 'strong' || value === 'high' || value === 'bullish') color = 'text-[#00ff00]';
    if (value === 'weak' || value === 'low' || value === 'bearish') color = 'text-[#ff4444]';
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded border border-[#1a1a1a] ${color} text-xs`}>
        {metric}: {value}
      </span>
    );
  };

  return (
    <div className="bg-[#0a0a0a] border border-[#1a1a1a] p-4 rounded-sm">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-[#ffd700]">{stock.symbol}</h3>
            <span className="text-[#666666] text-sm">{stock.name}</span>
          </div>
          <div className="text-sm text-[#666666]">
            {stock.sector} | {stock.industry}
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-[#666666] hover:text-[#00ff00] transition-colors"
        >
          {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
      </div>

      {/* Price Information */}
      <div className="grid grid-cols-2 gap-4 mb-2">
        <div>
          <div className="text-2xl font-mono">
            ${stock.current_price.toFixed(2)}
          </div>
          <div className={`text-sm ${isPositive ? 'text-[#00ff00]' : isNegative ? 'text-[#ff4444]' : 'text-[#666666]'}`}>
            {isPositive ? '+' : ''}{stock.daily_change_percent.toFixed(2)}%
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-[#666666]">Market Cap</div>
          <div className="text-lg font-mono">{stock.market_cap_formatted}</div>
        </div>
      </div>

      {/* Stock Chart */}
      <StockChart isPositive={isPositive} data={stock.historical_data} />

      {/* Trading Information */}
      <div className="grid grid-cols-2 gap-4 text-sm mb-4 mt-2">
        <div>
          <div className="text-[#666666]">Volume</div>
          <div className="font-mono">{formatNumber(stock.volume)}</div>
        </div>
        <div className="text-right">
          <div className="text-[#666666]">Day Range</div>
          <div className="font-mono">${stock.day_low.toFixed(2)} - ${stock.day_high.toFixed(2)}</div>
        </div>
      </div>

      {/* Expanded Analysis */}
      {expanded && stock.analysis && (
        <div className="mt-4 border-t border-[#1a1a1a] pt-4">
          {/* Key Metrics */}
          <div className="flex flex-wrap gap-2 mb-4">
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
          <div className="space-y-4">
            <div>
              <h4 className="text-[#ffd700] mb-1">Performance Summary</h4>
              <p className="text-sm text-[#666666]">{stock.analysis.performance_summary}</p>
            </div>
            <div>
              <h4 className="text-[#ffd700] mb-1">Trading Volume Analysis</h4>
              <p className="text-sm text-[#666666]">{stock.analysis.trading_volume_analysis}</p>
            </div>
            <div>
              <h4 className="text-[#ffd700] mb-1">Technical Signals</h4>
              <p className="text-sm text-[#666666]">{stock.analysis.technical_signals}</p>
            </div>
            <div>
              <h4 className="text-[#ffd700] mb-1">Market Sentiment</h4>
              <p className="text-sm text-[#666666]">{stock.analysis.market_sentiment}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockCard;
