# src/tests/test_parallel_processor.py

import pytest
import asyncio
from services.parallel_processor import ParallelStockProcessor
from data.stock_client import StockClient
import time

@pytest.mark.asyncio
async def test_single_stock_processing():
    """Test processing of a single stock"""
    processor = ParallelStockProcessor(max_workers=1)
    result = await processor.process_stock("AAPL")
    
    assert result is not None
    assert "symbol" in result
    assert result["symbol"] == "AAPL"
    assert "error" not in result
    assert "current_price" in result
    assert "volume" in result

@pytest.mark.asyncio
async def test_batch_processing():
    """Test processing multiple stocks in a batch"""
    processor = ParallelStockProcessor(max_workers=5)
    test_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    results = await processor.process_batch(test_symbols)
    
    assert len(results) == len(test_symbols)
    assert all("symbol" in result for result in results)
    assert all(result["symbol"] in test_symbols for result in results)

@pytest.mark.asyncio
async def test_parallel_performance():
    """Test performance of parallel processing vs sequential"""
    processor = ParallelStockProcessor(max_workers=5)
    test_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    # Test sequential processing
    start_time = time.time()
    sequential_results = []
    for symbol in test_symbols:
        result = await processor.process_stock(symbol)
        sequential_results.append(result)
    sequential_time = time.time() - start_time
    
    # Test parallel processing
    start_time = time.time()
    parallel_results = await processor.process_batch(test_symbols)
    parallel_time = time.time() - start_time
    
    # Parallel should be significantly faster
    assert parallel_time < sequential_time
    assert len(parallel_results) == len(sequential_results)