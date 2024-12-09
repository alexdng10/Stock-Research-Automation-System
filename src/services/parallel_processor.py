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
                self.logger.info(f"Processing {symbol}")
                start_time = datetime.now()
                
                # Get stock data
                stock_data = await self.stock_client.get_stock_details(symbol)
                
                # Store in database
                if "error" not in stock_data:
                    await self.database.update_stock_data(stock_data)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                self.logger.info(f"Processed {symbol} in {processing_time:.2f} seconds")
                
                return stock_data
                
            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {str(e)}")
                return {"symbol": symbol, "error": str(e)}

    async def process_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Process a batch of stocks in parallel"""
        tasks = []
        results = []
        
        # Create tasks for each symbol
        for symbol in symbols:
            task = asyncio.create_task(self.process_stock(symbol))
            tasks.append(task)
        
        # Wait for all tasks to complete
        completed, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.ALL_COMPLETED
        )
        
        # Collect results
        for task in completed:
            results.append(await task)
            
        return results

    async def process_with_progress(self, symbols: List[str], batch_size: int = 10) -> Dict[str, Any]:
        """Process all symbols in batches with progress tracking"""
        total_batches = (len(symbols) + batch_size - 1) // batch_size
        all_results = []
        failed_symbols = []
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_results = await self.process_batch(batch)
            
            # Track successes and failures
            for result in batch_results:
                if "error" in result:
                    failed_symbols.append(result["symbol"])
                else:
                    all_results.append(result)
            
            self.logger.info(f"Completed batch {(i//batch_size)+1}/{total_batches}")
        
        return {
            "processed_count": len(all_results),
            "failed_count": len(failed_symbols),
            "failed_symbols": failed_symbols,
            "results": all_results
        }