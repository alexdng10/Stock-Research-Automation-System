from fastapi import FastAPI
from src.services.llm_service import LLMService
from src.data.stock_client import StockClient
from src.services.query_processor import QueryProcessor

app = FastAPI(title="Stock Research Automation")
llm_service = LLMService()
stock_client = StockClient()
query_processor = QueryProcessor(llm_service, stock_client)

@app.get("/")
async def root():
    return {"message": "Stock Research Automation API"}

@app.post("/search")
async def search_stocks(query: str):
    """
    Search stocks based on natural language query
    """
    return await query_processor.process_query(query)

@app.get("/stocks/{symbol}")
async def get_stock_info(symbol: str):
    """
    Get detailed information about a specific stock
    """
    return await stock_client.get_stock_details(symbol)