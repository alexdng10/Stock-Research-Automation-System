# src/services/query_processor.py
from src.services.llm_service import LLMService
from src.data.stock_client import StockClient
import json

class QueryProcessor:
    def __init__(self, llm_service: LLMService, stock_client: StockClient):
        self.llm_service = llm_service
        self.stock_client = stock_client

    async def process_query(self, query: str):
        """
        Process natural language query and return relevant stock information
        """
        # Get structured criteria from LLM
        llm_response = await self.llm_service.process_query(query)
        
        try:
            # Parse LLM response to extract search criteria
            criteria = self._parse_llm_response(llm_response)
            
            # Search for stocks matching criteria
            results = await self._search_stocks(criteria)
            
            return {
                "query": query,
                "interpreted_criteria": criteria,
                "results": results
            }
        except Exception as e:
            return {"error": f"Failed to process query: {str(e)}"}

    def _parse_llm_response(self, llm_response: str) -> dict:
        """
        Parse LLM response into structured search criteria
        """
        try:
            # First try to parse as JSON if LLM returned structured data
            return json.loads(llm_response)
        except json.JSONDecodeError:
            # If not JSON, extract key information from text
            # This is a simple implementation - you might want to make this more sophisticated
            criteria = {
                "keywords": llm_response.lower().split(),
                "raw_response": llm_response
            }
            return criteria

    async def _search_stocks(self, criteria: dict) -> list:
        """
        Search for stocks matching the given criteria
        """
        # This is a placeholder implementation
        # You'll want to expand this based on your specific needs
        matching_stocks = []
        
        # Example: Search through some common stock symbols
        test_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        
        for symbol in test_symbols:
            stock_info = await self.stock_client.get_stock_details(symbol)
            
            # Simple keyword matching - you'll want to make this more sophisticated
            if self._matches_criteria(stock_info, criteria):
                matching_stocks.append(stock_info)

        return matching_stocks

    def _matches_criteria(self, stock_info: dict, criteria: dict) -> bool:
        """
        Check if a stock matches the search criteria
        """
        if "keywords" not in criteria:
            return True

        # Simple keyword matching - you'll want to make this more sophisticated
        text_to_search = " ".join([
            str(value).lower() 
            for value in stock_info.values() 
            if isinstance(value, (str, int, float))
        ])

        return any(
            keyword in text_to_search 
            for keyword in criteria["keywords"]
        )