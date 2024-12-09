// frontend/src/utils/apiClient.js
const API_BASE_URL = 'http://localhost:8000';

export const searchStocks = async (query) => {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });
  return response.json();
};

export const getStockDetails = async (symbol) => {
  const response = await fetch(`${API_BASE_URL}/stocks/${symbol}`);
  return response.json();
};