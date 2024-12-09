import { BarChart2, TrendingUp, Volume2 } from 'lucide-react';

const StockCard = ({ stock }) => {
  return (
    <div className="bg-[#1a1a1a] border border-gray-800 rounded p-4 hover:border-gray-700 transition-colors">
      {/* Header with Symbol and Change */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl text-yellow-500">{stock.symbol}</h3>
          <p className="text-gray-400 text-sm">{stock.name}</p>
          <p className="text-gray-500 text-xs mt-1">{stock.sector} | {stock.industry}</p>
        </div>
        <div className={`flex items-center ${
          stock.daily_change_percent >= 0 ? 'text-green-500' : 'text-red-500'
        }`}>
          <TrendingUp size={16} className="mr-1" />
          <span className="text-lg">
            {stock.daily_change_percent >= 0 ? '+' : ''}{stock.daily_change_percent}%
          </span>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2">
          <BarChart2 size={16} className="text-gray-500" />
          <div>
            <p className="text-gray-500 text-xs">PRICE</p>
            <p className="text-white font-mono">${stock.current_price}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Volume2 size={16} className="text-gray-500" />
          <div>
            <p className="text-gray-500 text-xs">VOLUME</p>
            <p className="text-white font-mono">{stock.volume?.toLocaleString()}</p>
          </div>
        </div>
        <div>
          <p className="text-gray-500 text-xs">MARKET CAP</p>
          <p className="text-white font-mono">{stock.market_cap_formatted}</p>
        </div>
        <div>
          <p className="text-gray-500 text-xs">DAY RANGE</p>
          <p className="text-white font-mono">${stock.day_low} - ${stock.day_high}</p>
        </div>
      </div>

      {/* Analysis Section */}
      {stock.analysis && (
        <div className="mt-4 pt-4 border-t border-gray-800">
          <h4 className="text-blue-400 text-sm mb-3">AI ANALYSIS</h4>
          <div className="space-y-3 text-sm">
            <p className="text-gray-300">{stock.analysis.performance_summary}</p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex gap-2 items-center">
                <span className="text-gray-500">TREND:</span>
                <span className={`
                  ${stock.analysis.key_metrics?.trend === 'bullish' ? 'text-green-500' : ''}
                  ${stock.analysis.key_metrics?.trend === 'bearish' ? 'text-red-500' : ''}
                  ${stock.analysis.key_metrics?.trend === 'neutral' ? 'text-yellow-500' : ''}
                `}>
                  {stock.analysis.key_metrics?.trend?.toUpperCase() || 'N/A'}
                </span>
              </div>
              <div className="flex gap-2 items-center">
                <span className="text-gray-500">VOLATILITY:</span>
                <span className="text-blue-400">
                  {stock.analysis.key_metrics?.volatility?.toUpperCase() || 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockCard;