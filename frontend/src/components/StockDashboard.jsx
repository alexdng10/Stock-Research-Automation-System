import { useState, useEffect } from 'react';
import StockCard from './StockCard';
import { stockAPI } from '../services/api';

const StockDashboard = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState([]);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const seconds = date.getSeconds();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const formattedHours = hours % 12 || 12;
    
    return `${String(formattedHours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')} ${ampm}`;
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    window.console.log('Starting search with query:', query);

    try {
      setLoading(true);
      setError(null);
      setResults([]); // Clear previous results

      // Wrap API call in try-catch to catch any network errors
      let data;
      try {
        window.console.log('Making API call...');
        data = await stockAPI.searchStocks(query);
        window.console.log('API response received:', data);
      } catch (apiError) {
        window.console.error('API call failed:', apiError);
        throw new Error(`API call failed: ${apiError.message}`);
      }

      if (!data) {
        window.console.error('No data received from API');
        throw new Error('No response from server');
      }

      if (data.error) {
        window.console.error('API returned error:', data.error);
        throw new Error(data.error);
      }

      if (!data.results || !Array.isArray(data.results)) {
        window.console.error('Invalid response format:', data);
        throw new Error('Invalid response format from server');
      }

      window.console.log('Setting results:', data.results);
      setResults(data.results);
      onSearch?.(data);

    } catch (err) {
      window.console.error('Search error:', err);
      setError(err.message || 'Failed to perform search. Please try again.');
    } finally {
      setLoading(false);
      window.console.log('Search completed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#111111] to-[#1a1a1a] text-[#2ecc71] p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8 border-b border-[#333333]/30 pb-4">
        <div className="flex items-center space-x-6">
          <div className="text-sm font-mono text-[#888888]">
            {formatTime(currentTime)}
          </div>
          <div className="text-[#2ecc71] font-bold tracking-wide">
            MARKET LIVE
          </div>
        </div>
        <div className="text-right text-xs font-mono text-[#888888] opacity-50">
          v1.0
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Main Content Area */}
        <div className="flex-1">
          {/* Search Section */}
          <div className="mb-10 relative z-50">
            <div className="flex justify-between items-center mb-3">
              <div className="text-[#f1c40f] font-bold tracking-wide text-sm">
                NATURAL LANGUAGE QUERY
              </div>
              <div className="text-[#888888] text-xs tracking-wide">
                AI-POWERED ANALYSIS
              </div>
            </div>
            <form onSubmit={handleSearch} className="flex gap-3 relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter a stock symbol..."
                className="flex-1 bg-[#111111]/60 border border-[#333333]/30 p-3 text-[#2ecc71] placeholder-[#444444] focus:outline-none focus:border-[#2ecc71]/50 rounded-lg backdrop-blur-md relative z-10"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-[#2ecc71]/10 hover:bg-[#2ecc71]/20 border border-[#2ecc71]/20 hover:border-[#2ecc71]/40 text-[#2ecc71] rounded-lg transition-all duration-200 backdrop-blur-md flex items-center justify-center relative z-10"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-[#e74c3c]/10 border border-[#e74c3c]/30 text-[#e74c3c] rounded-lg backdrop-blur-md">
              {error}
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-6 text-[#2ecc71]">
              <div className="loading-cursor inline-block mr-2">▋</div>
              Processing query...
            </div>
          )}

          {/* Results Grid */}
          <div className="grid grid-cols-1 gap-6 mb-6">
            {results.map((stock, index) => {
              window.console.log('Rendering stock card:', stock);
              return (
                <div key={`${stock.symbol}-${index}`} className="relative">
                  <StockCard stock={stock} />
                </div>
              );
            })}
          </div>
        </div>

        {/* Market Overview - Now integrated into the main layout */}
        <div className="lg:w-80 bg-[#111111]/40 backdrop-blur-md rounded-lg p-6 h-fit">
          <h3 className="font-bold mb-5 tracking-wide">MARKET OVERVIEW</h3>
          
          {/* Market Indices */}
          <div className="space-y-3 mb-6">
            <div className="flex justify-between items-center">
              <span className="text-[#888888]">S&P 500</span>
              <span className="value positive">+1.23%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#888888]">NASDAQ</span>
              <span className="value positive">+1.45%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#888888]">DOW</span>
              <span className="value negative">-0.32%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-[#888888]">VIX</span>
              <span className="value neutral">14.22</span>
            </div>
          </div>

          {/* Top Gainers */}
          <div className="mb-6">
            <h4 className="text-[#f1c40f] text-sm font-bold mb-3 tracking-wide">TOP GAINERS</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-[#888888]">AAPL</span>
                <span className="value positive">+3.45%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#888888]">MSFT</span>
                <span className="value positive">+2.78%</span>
              </div>
            </div>
          </div>

          {/* Top Losers */}
          <div>
            <h4 className="text-[#f1c40f] text-sm font-bold mb-3 tracking-wide">TOP LOSERS</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-[#888888]">META</span>
                <span className="value negative">-2.12%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-[#888888]">NFLX</span>
                <span className="value negative">-1.89%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDashboard;
