// frontend/src/services/api.js

const API_BASE_URL = 'http://localhost:8000';

export const stockAPI = {
    async searchStocks(query) {
      try {
        console.log('Searching for:', query); // Debug log
        const response = await fetch(`${API_BASE_URL}/search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          mode: 'cors',
          credentials: 'omit',
          body: JSON.stringify({ 
            query,
            include_historical: true, // Request historical data
            days: 365 // Get 1 year of historical data
          }),
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
        console.log('API Response:', data); // Debug log

        // Transform the data to ensure historical data is properly formatted
        if (data.results && Array.isArray(data.results)) {
          data.results = data.results.map(stock => ({
            ...stock,
            historical_data: stock.historical_data || {
              dates: [],
              prices: []
            }
          }));
        }

        return data;
      } catch (error) {
        console.error('Search error:', error);
        console.error('Error stack:', error.stack);
        throw error;
      }
    },
  
    async getStockDetails(symbol) {
      try {
        console.log('Fetching details for:', symbol); // Debug log
        const response = await fetch(`${API_BASE_URL}/stocks/${symbol}`, {
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
        console.log('API Response:', data); // Debug log

        // Ensure historical data is properly formatted
        if (data.historical_data) {
          data.historical_data = {
            dates: data.historical_data.dates || [],
            prices: data.historical_data.prices || []
          };
        }

        return data;
      } catch (error) {
        console.error('Stock details error:', error);
        console.error('Error stack:', error.stack);
        throw error;
      }
    }
};
