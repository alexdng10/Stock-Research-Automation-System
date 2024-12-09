# src/services/query_processor.py

from src.services.llm_service import LLMService
from src.data.stock_client import StockClient
from typing import Dict, List, Any
import json

class QueryProcessor:
    def __init__(self, llm_service: LLMService, stock_client: StockClient):
        self.llm_service = llm_service
        self.stock_client = stock_client
        self.stock_universe = [
            # Tech stocks
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "AMD", "INTC", "CSCO", "ORCL",
            # Data Center REITs
            "EQIX", "DLR", "AMT", "CCI", "QTS",
            # Nuclear/Energy
            "EXC", "DUK", "SO", "NEE", "NRG",
            # Add more sectors as needed
        ]

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and return relevant stock information"""
        try:
            # First, use LLM to parse the query
            parsed_query = await self._parse_query(query)
            
            # Fetch all stock data
            results = []
            for symbol in self.stock_universe:
                stock_info = await self.stock_client.get_stock_details(symbol)
                if "error" not in stock_info:
                    results.append(stock_info)

            # Apply filters based on parsed query
            filtered_results = self._apply_filters(results, parsed_query)
            
            # Sort results if specified
            sorted_results = self._sort_results(filtered_results, parsed_query)

            return {
                "query": query,
                "interpreted_as": parsed_query.get("description", ""),
                "results_count": len(sorted_results),
                "results": sorted_results[:10]  # Return top 10 results
            }

        except Exception as e:
            return {
                "error": f"Failed to process query: {str(e)}",
                "query": query,
                "results": []
            }

    async def _parse_query(self, query: str) -> Dict[str, Any]:
        """Use LLM to parse natural language query into structured format"""
        prompt = f"""
        Parse the following stock research query into structured format.
        Query: {query}
        
        Return JSON with these fields:
        - sectors: list of relevant sectors
        - market_cap_min: minimum market cap in billions (if mentioned)
        - market_cap_max: maximum market cap in billions (if mentioned)
        - volume_min: minimum trading volume (if mentioned)
        - keywords: list of key terms to match
        - sort_by: what to sort by (market_cap, volume, etc)
        - sort_order: asc or desc
        - description: human readable interpretation
        """
        
        try:
            response = await self.llm_service.process_query(prompt)
            return json.loads(response)
        except:
            # Fallback to basic keyword matching if LLM fails
            return {
                "keywords": query.lower().split(),
                "description": "Basic keyword search"
            }

    def _apply_filters(self, stocks: List[Dict], criteria: Dict) -> List[Dict]:
        """Apply filters based on parsed criteria"""
        filtered = stocks.copy()
        
        # Filter by market cap
        if criteria.get("market_cap_min"):
            min_cap = criteria["market_cap_min"] * 1e9  # Convert billions to actual value
            filtered = [s for s in filtered if s.get("market_cap", 0) >= min_cap]
            
        if criteria.get("market_cap_max"):
            max_cap = criteria["market_cap_max"] * 1e9
            filtered = [s for s in filtered if s.get("market_cap", 0) <= max_cap]

        # Filter by volume
        if criteria.get("volume_min"):
            filtered = [s for s in filtered if s.get("volume", 0) >= criteria["volume_min"]]

        # Filter by sector
        if criteria.get("sectors"):
            sectors = [s.lower() for s in criteria["sectors"]]
            filtered = [s for s in filtered if s.get("sector", "").lower() in sectors]

        # Filter by keywords
        if criteria.get("keywords"):
            keywords = [k.lower() for k in criteria["keywords"]]
            filtered = [s for s in filtered if any(
                k in s.get("description", "").lower() or 
                k in s.get("name", "").lower() or
                k in s.get("sector", "").lower() or
                k in s.get("industry", "").lower()
                for k in keywords
            )]

        return filtered

    def _sort_results(self, stocks: List[Dict], criteria: Dict) -> List[Dict]:
        """Sort results based on criteria"""
        sort_by = criteria.get("sort_by", "market_cap")
        sort_order = criteria.get("sort_order", "desc")
        
        reverse = sort_order.lower() == "desc"
        
        return sorted(
            stocks,
            key=lambda x: float(x.get(sort_by, 0) or 0),
            reverse=reverse
        )