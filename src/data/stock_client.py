# src/data/stock_client.py
import yfinance as yf
from src.config import Config
import pandas as pd
import numpy as np

class StockClient:
    def __init__(self):
        self.batch_size = Config.BATCH_SIZE

    def _convert_to_python_type(self, value):
        """Convert numpy/pandas types to native Python types"""
        if isinstance(value, (np.integer, np.int64)):
            return int(value)
        elif isinstance(value, (np.floating, np.float64)):
            return float(value)
        elif isinstance(value, np.bool_):
            return bool(value)
        elif isinstance(value, pd.Timestamp):
            return value.isoformat()
        elif isinstance(value, (pd.Series, np.ndarray)):
            return value.tolist()
        return value

    async def get_stock_details(self, symbol: str):
        """
        Fetch detailed stock information from Yahoo Finance
        """
        try:
            # Create Ticker object
            ticker = yf.Ticker(symbol)
            
            # Get current stock data
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return {
                    "error": f"No data available for {symbol}",
                    "symbol": symbol
                }

            # Convert numpy values to Python types
            current_price = self._convert_to_python_type(hist['Close'].iloc[-1]) if not hist.empty else None
            volume = self._convert_to_python_type(hist['Volume'].iloc[-1]) if not hist.empty else None
            
            # Build basic response
            response = {
                "symbol": symbol,
                "current_price": round(current_price, 2) if current_price else None,
                "volume": volume
            }
            
            # Try to get additional info
            try:
                info = ticker.info
                if info:
                    additional_info = {
                        "name": info.get('shortName', symbol),
                        "sector": info.get('sector', 'Unknown'),
                        "industry": info.get('industry', 'Unknown'),
                        "market_cap": self._convert_to_python_type(info.get('marketCap', 0)),
                        "pe_ratio": self._convert_to_python_type(info.get('forwardPE', None)),
                        "dividend_yield": self._convert_to_python_type(info.get('dividendYield', None)),
                        "52_week_high": self._convert_to_python_type(info.get('fiftyTwoWeekHigh', None)),
                        "52_week_low": self._convert_to_python_type(info.get('fiftyTwoWeekLow', None))
                    }
                    response.update(additional_info)
                    
                    # Format market cap to be more readable
                    if response["market_cap"]:
                        if response["market_cap"] >= 1_000_000_000_000:  # Trillion
                            response["market_cap_formatted"] = f"${response['market_cap']/1_000_000_000_000:.2f}T"
                        elif response["market_cap"] >= 1_000_000_000:  # Billion
                            response["market_cap_formatted"] = f"${response['market_cap']/1_000_000_000:.2f}B"
                        elif response["market_cap"] >= 1_000_000:  # Million
                            response["market_cap_formatted"] = f"${response['market_cap']/1_000_000:.2f}M"
            except Exception as e:
                response["info_error"] = str(e)

            return response

        except Exception as e:
            return {
                "error": f"Failed to fetch data for {symbol}: {str(e)}",
                "symbol": symbol
            }