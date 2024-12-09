import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

const StockDashboard = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [debugInfo, setDebugInfo] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setDebugInfo(null);
    
    try {
      console.log('Sending request with query:', query);
      
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query }),
      });

      const data = await response.json();
      console.log('Received response:', data);
      setDebugInfo(data); // Store full response for debugging

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
      console.error('Search error:', err);
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

        {/* Debug Info */}
        {debugInfo && (
          <div className="mt-4 p-4 bg-gray-900 rounded border border-gray-800">
            <h3 className="text-yellow-500 mb-2">Debug Info:</h3>
            <pre className="text-sm text-gray-400 overflow-auto">
              {JSON.stringify(debugInfo, null, 2)}
            </pre>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-900/20 border border-red-800 rounded">
            <span className="text-red-500">{error}</span>
          </div>
        )}

        {/* Results */}
        {results && results.length > 0 && (
          <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
            {results.map((stock, index) => (
              <div key={stock.symbol || index} className="bg-[#1a1a1a] border border-gray-800 rounded p-4">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl text-yellow-500">{stock.symbol}</h3>
                    <p className="text-gray-400 text-sm">{stock.name}</p>
                  </div>
                  <div className={`text-lg ${stock.daily_change_percent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {stock.daily_change_percent >= 0 ? '+' : ''}{stock.daily_change_percent}%
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-500 text-sm">PRICE</p>
                    <p className="text-white">${stock.current_price}</p>
                  </div>
                  <div>
                    <p className="text-gray-500 text-sm">VOLUME</p>
                    <p className="text-white">{stock.volume?.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StockDashboard;