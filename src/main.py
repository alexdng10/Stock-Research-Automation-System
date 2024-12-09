# main.py

from fastapi import FastAPI, BackgroundTasks
from src.services.llm_service import LLMService
from src.data.stock_client import StockClient
from src.services.query_processor import QueryProcessor
from src.services.parallel_processor import ParallelStockProcessor
from typing import List, Optional
import asyncio

app = FastAPI(title="Stock Research Automation")
llm_service = LLMService()
stock_client = StockClient()
query_processor = QueryProcessor(llm_service, stock_client)
parallel_processor = ParallelStockProcessor(max_workers=5)

@app.get("/")
async def root():
    return {"message": "Stock Research Automation API"}

@app.post("/search")
async def search_stocks(query: str):
    """Search stocks based on natural language query"""
    return await query_processor.process_query(query)

@app.get("/stocks/{symbol}")
async def get_stock_info(symbol: str):
    """Get detailed information about a specific stock"""
    return await stock_client.get_stock_details(symbol)

@app.post("/process-stocks")
async def process_stocks(symbols: List[str], batch_size: Optional[int] = 10):
    """Process multiple stocks in parallel with efficient batching"""
    return await parallel_processor.process_with_progress(symbols, batch_size)

@app.get("/batch-status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of a batch processing job"""
    # Implement batch status tracking
    pass