# src/services/parallel_processor.py

import asyncio
from typing import List, Dict, Any
from src.data.stock_client import StockClient
from src.data.database import Database
import logging
from datetime import datetime

class ParallelStockProcessor:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.stock_client = StockClient()
        self.database = Database()
        self.processing_semaphore = asyncio.Semaphore(max_workers)
        self.logger = logging.getLogger(__name__)

    async def process_stock(self, symbol: str) -> Dict[str, Any]:
        """Process a single stock with error handling and retries"""
        async with self.processing_semaphore:  # Limit concurrent processing
            try:
                stock_data = await self.stock_client.get_stock_details(symbol)
                
                # Store in database if no error
                if "error" not in stock_data:
                    await self.database.update_stock_data(stock_data)
                
                return stock_data
                
            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {str(e)}")
                return {"symbol": symbol, "error": str(e)}

    async def process_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Process a batch of stocks in parallel"""
        tasks = [self.process_stock(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Batch processing error: {str(result)}")
                continue
            processed_results.append(result)
            
        return processed_results