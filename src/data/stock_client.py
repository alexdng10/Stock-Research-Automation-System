# src/data/stock_client.py

import yfinance as yf
from src.config import Config
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

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

    def _get_historical_data(self, symbol: str, days: int = 365) -> Optional[Dict[str, List]]:
        """Fetch historical data using yfinance download function"""
        try:
            # Calculate start and end dates
            end_date = datetime.now()  # Today
            start_date = end_date - timedelta(days=days)
            
            # Use yfinance download function
            hist_data = yf.download(
                symbol,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                progress=False,
                show_errors=False
            )
            
            if hist_data.empty:
                return None
            
            # Filter out any future dates and convert to lists
            current_date = datetime.now().date()
            dates = []
            prices = []
            
            for date, row in hist_data.iterrows():
                if date.date() <= current_date:  # Only include dates up to today
                    dates.append(date.strftime('%Y-%m-%d'))
                    prices.append(round(float(row['Close']), 2))
            
            # Validate filtered data
            if not dates or not prices:
                return None
                
            if len(dates) != len(prices):
                return None
            
            return {
                "dates": dates,
                "prices": prices
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    async def get_stock_details(self, symbol: str, include_historical: bool = True, days: int = 365) -> Dict[str, Any]:
        """Fetch detailed stock information from Yahoo Finance"""
        max_retries = 3
        retry_delay = 0.5  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add delay between attempts
                if attempt > 0:
                    time.sleep(retry_delay)
                
                logger.info(f"Fetching data for {symbol}")
                ticker = yf.Ticker(symbol)

                # Get current price data (2 days for calculating daily change)
                hist = ticker.history(period="2d")
                if hist.empty:
                    logger.warning(f"No current price data available for {symbol}")
                    return {
                        "error": f"No data available for {symbol}",
                        "symbol": symbol
                    }

                # Get the most recent day's data
                latest_data = hist.iloc[-1]
                
                # Build base response
                response = {
                    "symbol": symbol,
                    "current_price": round(self._safe_convert(latest_data['Close']), 2),
                    "volume": self._safe_convert(latest_data['Volume']),
                    "day_high": round(self._safe_convert(latest_data['High']), 2),
                    "day_low": round(self._safe_convert(latest_data['Low']), 2),
                    "day_open": round(self._safe_convert(latest_data['Open']), 2)
                }

                # Fetch and add historical data if requested
                if include_historical:
                    historical_data = self._get_historical_data(symbol, days)
                    if historical_data:
                        response["historical_data"] = historical_data
                        logger.info(f"Historical data added to response for {symbol}")
                    else:
                        logger.warning(f"Failed to get historical data for {symbol}")

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
                    logger.error(f"Error fetching additional info for {symbol}: {str(e)}")

                # Calculate daily change
                if all(k in response for k in ['current_price', 'day_open']):
                    daily_change = response['current_price'] - response['day_open']
                    daily_change_percent = (daily_change / response['day_open']) * 100
                    response.update({
                        "daily_change": round(daily_change, 2),
                        "daily_change_percent": round(daily_change_percent, 2)
                    })

                # Log the final response structure
                logger.info(f"Response structure for {symbol}:")
                logger.info(f"Keys in response: {list(response.keys())}")
                if "historical_data" in response:
                    logger.info(f"Historical data present with {len(response['historical_data']['dates'])} data points")
                else:
                    logger.info(f"No historical data in response for {symbol}")

                return response

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts: {str(e)}")
                    return {
                        "error": f"Failed to fetch data for {symbol}",
                        "symbol": symbol
                    }
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                continue
