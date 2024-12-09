# main.py

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel  # Added this import
from typing import List, Optional
import asyncio
import logging
from src.services.llm_service import LLMService
from src.data.stock_client import StockClient
from src.services.query_processor import QueryProcessor
from src.services.parallel_processor import ParallelStockProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Define the Pydantic model for the search query
class SearchQuery(BaseModel):
    query: str

app = FastAPI(title="Stock Research Automation")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_service = LLMService()
stock_client = StockClient()
query_processor = QueryProcessor(llm_service, stock_client)
parallel_processor = ParallelStockProcessor(max_workers=5)

@app.get("/")
async def root():
    return {"message": "Stock Research Automation API"}

@app.post("/search")
async def search_stocks(search_query: SearchQuery):
    """Search stocks based on natural language query"""
    return await query_processor.process_query(search_query.query)

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