// frontend/src/services/api.js

export const stockAPI = {
    async searchStocks(query) {
      try {
        const response = await fetch('http://localhost:8000/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query }),
        });
        
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('Search error:', error);
        throw error;
      }
    },
  
    async getStockDetails(symbol) {
      try {
        const response = await fetch(`http://localhost:8000/stocks/${symbol}`);
        
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('Stock details error:', error);
        throw error;
      }
    }
  };