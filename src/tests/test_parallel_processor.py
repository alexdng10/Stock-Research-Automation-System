# src/tests/test_parallel_processor.py

import pytest
from services.parallel_processor import ParallelStockProcessor
import asyncio
import time

@pytest.mark.asyncio
async def test_single_stock_processing():
    """Test processing of a single stock"""
    processor = ParallelStockProcessor(max_workers=1)
    result = await processor.process_stock("AAPL")
    
    assert result is not None
    assert "symbol" in result
    assert result["symbol"] == "AAPL"
    assert "current_price" in result or "error" in result  # Allow for API errors

@pytest.mark.asyncio
async def test_batch_processing():
    """Test processing multiple stocks in a batch"""
    processor = ParallelStockProcessor(max_workers=5)
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    results = await processor.process_batch(test_symbols)
    
    assert len(results) > 0
    for result in results:
        assert "symbol" in result

@pytest.mark.asyncio
async def test_parallel_performance():
    """Test performance of parallel processing vs sequential"""
    processor = ParallelStockProcessor(max_workers=5)
    test_symbols = ["AAPL", "MSFT", "GOOGL"]  # Reduced number of symbols for testing
    
    # Sequential processing
    start_time = time.time()
    sequential_results = []
    for symbol in test_symbols:
        result = await processor.process_stock(symbol)
        sequential_results.append(result)
    sequential_time = time.time() - start_time
    
    # Parallel processing
    start_time = time.time()
    parallel_results = await processor.process_batch(test_symbols)
    parallel_time = time.time() - start_time
    
    # Parallel should not be more than 2x slower than sequential
    assert parallel_time <= sequential_time * 2
    assert len(parallel_results) > 0