# src/data/stock_client.py

import yfinance as yf
from src.config import Config
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import time

class StockClient:
    def __init__(self):
        self.batch_size = Config.BATCH_SIZE

    def _safe_convert(self, value: Any) -> Any:
        """Safely convert numpy/pandas types to JSON-serializable Python types"""
        if pd.isna(value):
            return None
        if isinstance(value, (np.integer, np.int64)):
            return int(value)
        if isinstance(value, (np.floating, np.float64)):
            return float(value)
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if isinstance(value, (pd.Series, np.ndarray)):
            return [self._safe_convert(x) for x in value]
        return value

    def _format_market_cap(self, market_cap: Optional[float]) -> str:
        """Format market cap into human-readable string"""
        if not market_cap:
            return None
        
        if market_cap >= 1e12:  # Trillion
            return f"${market_cap/1e12:.2f}T"
        if market_cap >= 1e9:   # Billion
            return f"${market_cap/1e9:.2f}B"
        if market_cap >= 1e6:   # Million
            return f"${market_cap/1e6:.2f}M"
        return f"${market_cap:.2f}"

    async def get_stock_details(self, symbol: str) -> Dict[str, Any]:
        """Fetch detailed stock information from Yahoo Finance"""
        max_retries = 3
        retry_delay = 0.5  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add delay between attempts
                if attempt > 0:
                    time.sleep(retry_delay)
                
                ticker = yf.Ticker(symbol)
                # Get 2 days for current price data
                hist = ticker.history(period="2d")
                # Get 30 days for historical chart data
                hist_30d = ticker.history(period="30d")
                
                if hist.empty:
                    print(f"No data available for {symbol}")
                    return {
                        "error": f"No data available for {symbol}",
                        "symbol": symbol
                    }

                # Get the most recent day's data
                latest_data = hist.iloc[-1]
                
                response = {
                    "symbol": symbol,
                    "current_price": round(self._safe_convert(latest_data['Close']), 2),
                    "volume": self._safe_convert(latest_data['Volume']),
                    "day_high": round(self._safe_convert(latest_data['High']), 2),
                    "day_low": round(self._safe_convert(latest_data['Low']), 2),
                    "day_open": round(self._safe_convert(latest_data['Open']), 2)
                }

                # Add historical data for the chart
                if not hist_30d.empty:
                    historical_data = {
                        "labels": [date.strftime('%Y-%m-%d') for date in hist_30d.index],
                        "prices": [round(price, 2) for price in hist_30d['Close'].tolist()]
                    }
                    response["historical_data"] = historical_data

                # Try to get additional info
                try:
                    info = ticker.fast_info
                    if info:
                        market_cap = self._safe_convert(getattr(info, 'market_cap', None))
                        if market_cap:
                            response.update({
                                "market_cap": market_cap,
                                "market_cap_formatted": self._format_market_cap(market_cap)
                            })
                except Exception as e:
                    print(f"Error fetching additional info for {symbol}: {str(e)}")

                # Calculate daily change
                if all(k in response for k in ['current_price', 'day_open']):
                    daily_change = response['current_price'] - response['day_open']
                    daily_change_percent = (daily_change / response['day_open']) * 100
                    response.update({
                        "daily_change": round(daily_change, 2),
                        "daily_change_percent": round(daily_change_percent, 2)
                    })

                return response

            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch data for {symbol} after {max_retries} attempts: {str(e)}")
                    return {
                        "error": f"Failed to fetch data for {symbol}",
                        "symbol": symbol
                    }
                continue
