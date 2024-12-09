import { useState } from 'react';
import { Search } from 'lucide-react';
import StockCard from './StockCard';

const StockDashboard = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });
      
      const data = await response.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      if (!data.results || !Array.isArray(data.results)) {
        setError('Invalid response format');
        return;
      }

      setResults(data.results);
      
      if (data.results.length === 0) {
        setError('No matching stocks found');
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-mono">
      {/* Header */}
      <div className="bg-[#1a1a1a] p-3 border-b border-gray-800">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <span className="text-yellow-500">{new Date().toLocaleTimeString()}</span>
            <span className="text-green-500">MARKET LIVE</span>
          </div>
          <span className="text-gray-500">TERMINAL v1.0</span>
        </div>
      </div>

      {/* Search Section */}
      <div className="p-6">
        <div className="bg-[#1a1a1a] rounded p-4">
          <div className="flex justify-between mb-4">
            <span className="text-yellow-500 text-xl">NATURAL LANGUAGE QUERY</span>
            <span className="text-gray-500">AI-POWERED ANALYSIS</span>
          </div>
          
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Show me tech stocks..."
              className="flex-1 bg-black border border-gray-800 p-2 text-white rounded"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="bg-yellow-500 text-black px-4 py-2 rounded flex items-center gap-2"
            >
              {loading ? 'SEARCHING...' : 'EXECUTE'}
            </button>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-900/20 border border-red-800 rounded">
            <span className="text-red-500">{error}</span>
          </div>
        )}

        {/* Results Grid */}
        {results && results.length > 0 && (
          <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
            {results.map((stock, index) => (
              <StockCard key={stock.symbol || index} stock={stock} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StockDashboard;