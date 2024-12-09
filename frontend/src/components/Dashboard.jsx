import React from 'react';
import StockDashboard from './StockDashboard';

const Dashboard = () => {
  const handleSearch = (data) => {
    console.log('Search results:', data);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <StockDashboard onSearch={handleSearch} />
    </div>
  );
};

export default Dashboard;
