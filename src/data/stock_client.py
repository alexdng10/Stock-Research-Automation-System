import yfinance as yf
import pandas as pd

class StockClient:
    def __init__(self):
        self.batch_size = Config.BATCH_SIZE
    
    async def get_stock_details(self, symbol: str):
        """
        Fetch detailed stock information from Yahoo Finance
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            return {
                "symbol": symbol,
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "volume": info.get("volume"),
                "description": info.get("longBusinessSummary")
            }
        except Exception as e:
            return {"error": f"Failed to fetch stock details: {str(e)}"}