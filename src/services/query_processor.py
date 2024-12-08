# src/services/query_processor.py
import json
from src.services.llm_service import LLMService
from src.data.stock_client import StockClient

class QueryProcessor:
    def __init__(self, llm_service: LLMService, stock_client: StockClient):
        self.llm_service = llm_service
        self.stock_client = stock_client
        # Extended list of tech stocks
        self.tech_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", 
                           "TSLA", "TSM", "ASML", "AVGO", "ORCL", "CSCO", "ADBE", "CRM"]

    async def process_query(self, query: str):
        """
        Process natural language query and return relevant stock information
        """
        try:
            # Get stocks data first
            results = []
            for symbol in self.tech_stocks:
                stock_info = await self.stock_client.get_stock_details(symbol)
                if "error" not in stock_info:
                    results.append(stock_info)

            # Filter results based on query
            if "market cap" in query.lower():
                results = sorted(results, 
                               key=lambda x: float(x.get("market_cap", 0)) if isinstance(x.get("market_cap"), (int, float)) else 0, 
                               reverse=True)

            return {
                "query": query,
                "results_count": len(results),
                "results": results[:5]  # Return top 5 results
            }

        except Exception as e:
            return {
                "error": f"Failed to process query: {str(e)}",
                "query": query,
                "results": []
            }

    def _filter_by_sector(self, stocks, sector):
        """Helper method to filter stocks by sector"""
        return [stock for stock in stocks if stock.get("sector", "").lower() == sector.lower()]