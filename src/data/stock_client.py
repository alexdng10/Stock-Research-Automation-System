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
        try:
            # Create ticker with a small delay to avoid rate limiting
            time.sleep(0.1)
            ticker = yf.Ticker(symbol)
            
            # Get historical data for last 2 days to ensure we have data
            hist = ticker.history(period="2d")
            if hist.empty:
                return {
                    "error": f"No data available for {symbol}",
                    "symbol": symbol
                }

            # Get the most recent day's data
            latest_data = hist.iloc[-1]
            
            # Build base response with current price and volume
            response = {
                "symbol": symbol,
                "current_price": round(self._safe_convert(latest_data['Close']), 2),
                "volume": self._safe_convert(latest_data['Volume']),
                "day_high": round(self._safe_convert(latest_data['High']), 2),
                "day_low": round(self._safe_convert(latest_data['Low']), 2),
                "day_open": round(self._safe_convert(latest_data['Open']), 2)
            }

            # Try to get additional info with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    time.sleep(0.2)  # Add delay between retries
                    info = ticker.fast_info  # Use fast_info instead of info
                    if info:
                        market_cap = self._safe_convert(getattr(info, 'market_cap', None))
                        additional_info = {
                            "market_cap": market_cap,
                            "market_cap_formatted": self._format_market_cap(market_cap),
                            "last_dividend": self._safe_convert(getattr(info, 'last_dividend', None)),
                            "shares": self._safe_convert(getattr(info, 'shares', None))
                        }
                        response.update({k: v for k, v in additional_info.items() if v is not None})
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        response["info_error"] = f"Failed to fetch additional info after {max_retries} attempts"

            # Calculate daily change
            if 'current_price' in response and 'day_open' in response:
                daily_change = response['current_price'] - response['day_open']
                daily_change_percent = (daily_change / response['day_open']) * 100
                response.update({
                    "daily_change": round(daily_change, 2),
                    "daily_change_percent": round(daily_change_percent, 2)
                })

            return response

        except Exception as e:
            return {
                "error": f"Failed to fetch data for {symbol}: {str(e)}",
                "symbol": symbol
            }