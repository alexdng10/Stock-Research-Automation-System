# main.py

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import logging
import sys
import traceback
from src.services.llm_service import LLMService
from src.data.stock_client import StockClient
from src.services.query_processor import QueryProcessor
from src.services.parallel_processor import ParallelStockProcessor

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Define the Pydantic model for the search query
class SearchQuery(BaseModel):
    query: str
    include_historical: Optional[bool] = True
    days: Optional[int] = 365

app = FastAPI(title="Stock Research Automation")

# Add CORS middleware with more permissive configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

@app.options("/{path:path}")
async def options_handler(request: Request):
    """Handle preflight requests"""
    origin = request.headers.get("origin", "*")
    response = JSONResponse(content={})
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept, Origin"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

try:
    logger.info("Initializing services...")
    llm_service = LLMService()
    stock_client = StockClient()
    query_processor = QueryProcessor(llm_service, stock_client)
    parallel_processor = ParallelStockProcessor(max_workers=5)
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    logger.error(traceback.format_exc())
    raise

@app.get("/")
async def root():
    return {"message": "Stock Research Automation API"}

@app.post("/search")
async def search_stocks(search_query: SearchQuery, request: Request):
    """Search stocks based on natural language query"""
    try:
        logger.info(f"Processing search query: {search_query.query}")
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Include historical: {search_query.include_historical}, Days: {search_query.days}")
        
        # Pass historical data parameters to the query processor
        result = await query_processor.process_query(
            search_query.query,
            include_historical=search_query.include_historical,
            days=search_query.days
        )
        logger.info(f"Search completed successfully")
        logger.debug(f"Search result: {result}")
        
        response = JSONResponse(content=result)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        logger.error(f"Error processing search query: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{symbol}")
async def get_stock_info(symbol: str, include_historical: Optional[bool] = True, days: Optional[int] = 365):
    """Get detailed information about a specific stock"""
    try:
        logger.info(f"Fetching stock info for symbol: {symbol}")
        logger.debug(f"Include historical: {include_historical}, Days: {days}")
        result = await stock_client.get_stock_details(symbol, include_historical=include_historical, days=days)
        logger.info(f"Successfully retrieved stock info for {symbol}")
        return result
    except Exception as e:
        logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-stocks")
async def process_stocks(symbols: List[str], batch_size: Optional[int] = 10):
    """Process multiple stocks in parallel with efficient batching"""
    try:
        logger.info(f"Processing batch of stocks: {symbols}")
        result = await parallel_processor.process_with_progress(symbols, batch_size)
        logger.info("Batch processing completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing batch of stocks: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/batch-status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of a batch processing job"""
    # Implement batch status tracking
    pass

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
