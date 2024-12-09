import { useState } from 'react';
import StockCard from './StockCard';

const StockDashboard = ({ onSearch }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Search request failed');
      }

      const data = await response.json();
      setResults(data.results || []);
      onSearch?.(data);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to perform search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#00ff00] p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 border-b border-[#1a1a1a] pb-4">
        <div className="flex items-center space-x-4">
          <div className="text-sm font-mono">
            {new Date().toLocaleTimeString()} PM
          </div>
          <div className="text-[#00ff00] font-bold">
            MARKET LIVE
          </div>
        </div>
        <div className="text-right text-sm font-mono">
          TERMINAL v1.0
        </div>
      </div>

      {/* Search Section */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <div className="text-[#ffd700] font-bold">
            NATURAL LANGUAGE QUERY
          </div>
          <div className="text-[#666666]">
            AI-POWERED ANALYSIS
          </div>
        </div>
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Show me tech stocks..."
            className="flex-1 bg-[#0a0a0a] border border-[#1a1a1a] p-2 text-[#00ff00] placeholder-[#333333] focus:outline-none focus:border-[#00ff00]"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-[#1a1a1a] text-[#00ff00] px-4 py-2 hover:bg-[#2a2a2a] transition-colors disabled:opacity-50"
          >
            EXECUTE
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-[#ff000022] border border-[#ff0000] text-[#ff0000]">
          {error}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-4 text-[#00ff00]">
          Processing query...
        </div>
      )}

      {/* Results Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {results.map((stock, index) => (
          <StockCard key={`${stock.symbol}-${index}`} stock={stock} />
        ))}
      </div>

      {/* Market Overview */}
      <div className="fixed top-4 right-4 w-64 bg-[#0a0a0a] border border-[#1a1a1a] p-4">
        <h3 className="text-[#ffd700] font-bold mb-4">MARKET OVERVIEW</h3>
        
        {/* Market Indices */}
        <div className="space-y-2 mb-4">
          <div className="flex justify-between">
            <span>S&P 500</span>
            <span className="text-[#00ff00]">+1.23%</span>
          </div>
          <div className="flex justify-between">
            <span>NASDAQ</span>
            <span className="text-[#00ff00]">+1.45%</span>
          </div>
          <div className="flex justify-between">
            <span>DOW</span>
            <span className="text-[#ff4444]">-0.32%</span>
          </div>
          <div className="flex justify-between">
            <span>VIX</span>
            <span>14.22</span>
          </div>
        </div>

        {/* Top Gainers */}
        <div className="mb-4">
          <h4 className="text-[#ffd700] mb-2">TOP GAINERS</h4>
          <div className="space-y-1">
            <div className="flex justify-between">
              <span>AAPL</span>
              <span className="text-[#00ff00]">+3.45%</span>
            </div>
            <div className="flex justify-between">
              <span>MSFT</span>
              <span className="text-[#00ff00]">+2.78%</span>
            </div>
          </div>
        </div>

        {/* Top Losers */}
        <div>
          <h4 className="text-[#ffd700] mb-2">TOP LOSERS</h4>
          <div className="space-y-1">
            <div className="flex justify-between">
              <span>META</span>
              <span className="text-[#ff4444]">-2.12%</span>
            </div>
            <div className="flex justify-between">
              <span>NFLX</span>
              <span className="text-[#ff4444]">-1.89%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDashboard;
