// frontend/src/services/api.js

export const stockAPI = {
    async searchStocks(query) {
      try {
        const response = await fetch('http://localhost:8001/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          mode: 'cors',
          credentials: 'omit',
          body: JSON.stringify({ query }),
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('API Error:', response.status, errorText);
          throw new Error(`API Error: ${response.status} - ${errorText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          console.error('Invalid content type:', contentType);
          throw new Error('Invalid response format: not JSON');
        }

        const data = await response.json();
        console.log('API Response:', data);
        return data;
      } catch (error) {
        console.error('Search error:', error);
        console.error('Error stack:', error.stack);
        throw error;
      }
    },
  
    async getStockDetails(symbol) {
      try {
        const response = await fetch(`http://localhost:8001/stocks/${symbol}`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
          mode: 'cors',
          credentials: 'omit',
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('API Error:', response.status, errorText);
          throw new Error(`API Error: ${response.status} - ${errorText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          console.error('Invalid content type:', contentType);
          throw new Error('Invalid response format: not JSON');
        }

        const data = await response.json();
        console.log('API Response:', data);
        return data;
      } catch (error) {
        console.error('Stock details error:', error);
        console.error('Error stack:', error.stack);
        throw error;
      }
    }
  };
