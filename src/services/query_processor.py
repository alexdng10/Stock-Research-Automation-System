# src/services/query_processor.py

from src.services.llm_service import LLMService
from src.data.stock_client import StockClient
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class StockInfo:
    """Stock information data class"""
    def __init__(self, symbol: str, sector: str, industry: str, name: str = ""):
        self.symbol = symbol
        self.sector = sector
        self.industry = industry
        self.name = name

class QueryProcessor:
    def __init__(self, llm_service: LLMService, stock_client: StockClient):
        self.llm_service = llm_service
        self.stock_client = stock_client
        
        # Enhanced stock universe with sector and industry information
        self.stock_universe = {
            # Technology Sector
            "AAPL": StockInfo("AAPL", "Technology", "Consumer Electronics", "Apple Inc."),
            "MSFT": StockInfo("MSFT", "Technology", "Software", "Microsoft Corporation"),
            "GOOG": StockInfo("GOOG", "Technology", "Internet Services", "Alphabet Inc."),
            "AMZN": StockInfo("AMZN", "Technology", "E-Commerce", "Amazon.com Inc."),
            "META": StockInfo("META", "Technology", "Social Media", "Meta Platforms Inc."),
            "NVDA": StockInfo("NVDA", "Technology", "Semiconductors", "NVIDIA Corporation"),
            "AMD": StockInfo("AMD", "Technology", "Semiconductors", "Advanced Micro Devices"),
            "INTC": StockInfo("INTC", "Technology", "Semiconductors", "Intel Corporation"),
            
            # Data Centers & Cloud
            "EQIX": StockInfo("EQIX", "Real Estate", "Data Centers", "Equinix Inc."),
            "DLR": StockInfo("DLR", "Real Estate", "Data Centers", "Digital Realty Trust"),
            "CRM": StockInfo("CRM", "Technology", "Software", "Salesforce Inc."),
            
            # Semiconductors
            "TSM": StockInfo("TSM", "Technology", "Semiconductors", "Taiwan Semiconductor"),
            "ASML": StockInfo("ASML", "Technology", "Semiconductor Equipment", "ASML Holding"),
            "AMAT": StockInfo("AMAT", "Technology", "Semiconductor Equipment", "Applied Materials"),
            
            # Energy Sector
            "XOM": StockInfo("XOM", "Energy", "Oil & Gas", "Exxon Mobil Corporation"),
            "CVX": StockInfo("CVX", "Energy", "Oil & Gas", "Chevron Corporation"),
            
            # Financial Sector
            "JPM": StockInfo("JPM", "Finance", "Banking", "JPMorgan Chase & Co."),
            "BAC": StockInfo("BAC", "Finance", "Banking", "Bank of America Corp."),
            "GS": StockInfo("GS", "Finance", "Investment Banking", "Goldman Sachs Group")
        }

    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and return relevant stock information"""
        try:
            logger.info(f"Processing query: {query}")
            parsed_query = await self._parse_query(query)
            logger.debug(f"Parsed query: {parsed_query}")
            
            # Fetch live stock data and merge with static info
            results = await self._fetch_stock_data()
            
            if not results:
                return {
                    "query": query,
                    "error": "No stock data available at the moment",
                    "results": []
                }
            
            # Apply filters
            filtered_results = self._apply_filters(results, parsed_query)
            
            # Sort results if specified
            if parsed_query.get("sort_by"):
                filtered_results = self._sort_results(filtered_results, parsed_query)
            
            response = {
                "query": query,
                "interpreted_as": parsed_query.get("description", ""),
                "results_count": len(filtered_results),
                "results": filtered_results[:10]  # Return top 10 results
            }
            
            logger.info(f"Found {len(filtered_results)} matching stocks")
            return response

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "error": f"Failed to process query: {str(e)}",
                "query": query,
                "results": []
            }

    async def _fetch_stock_data(self) -> List[Dict[str, Any]]:
        """Fetch live stock data and merge with static information"""
        results = []
        
        for symbol, info in self.stock_universe.items():
            stock_data = await self.stock_client.get_stock_details(symbol)
            
            if "error" not in stock_data:
                # Merge static info with live data
                stock_data.update({
                    "name": info.name,
                    "sector": info.sector,
                    "industry": info.industry
                })
                results.append(stock_data)
        
        return results

    async def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured format"""
        query_lower = query.lower()
        
        # Common keywords mapping
        sector_keywords = {
            "tech": "Technology",
            "technology": "Technology",
            "finance": "Finance",
            "financial": "Finance",
            "energy": "Energy",
            "real estate": "Real Estate"
        }
        
        industry_keywords = {
            "semiconductor": "Semiconductors",
            "software": "Software",
            "banking": "Banking",
            "data center": "Data Centers"
        }
        
        try:
            # Try LLM parsing first
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
            
            response = await self.llm_service.process_query(prompt)
            if isinstance(response, dict):
                return response
            return json.loads(response)
            
        except Exception as e:
            logger.warning(f"LLM parsing failed, using fallback: {str(e)}")
            
            # Enhanced fallback parsing
            sectors = []
            for keyword, sector in sector_keywords.items():
                if keyword in query_lower:
                    sectors.append(sector)
            
            industries = []
            for keyword, industry in industry_keywords.items():
                if keyword in query_lower:
                    industries.append(industry)
            
            # Default response
            return {
                "sectors": sectors,
                "industries": industries,
                "keywords": query_lower.split(),
                "description": f"Searching for stocks in sectors: {', '.join(sectors) or 'all'}"
            }

    def _apply_filters(self, stocks: List[Dict], criteria: Dict) -> List[Dict]:
        """Apply all filters to stock list"""
        filtered = stocks.copy()
        
        # Sector filter
        if criteria.get("sectors"):
            filtered = [s for s in filtered 
                       if s.get("sector") in criteria["sectors"]]
        
        # Industry filter
        if criteria.get("industries"):
            filtered = [s for s in filtered 
                       if s.get("industry") in criteria["industries"]]
        
        # Market cap filter
        if criteria.get("market_cap_min"):
            min_cap = criteria["market_cap_min"] * 1e9
            filtered = [s for s in filtered 
                       if s.get("market_cap", 0) >= min_cap]
        
        if criteria.get("market_cap_max"):
            max_cap = criteria["market_cap_max"] * 1e9
            filtered = [s for s in filtered 
                       if s.get("market_cap", 0) <= max_cap]
        
        # Volume filter
        if criteria.get("volume_min"):
            filtered = [s for s in filtered 
                       if s.get("volume", 0) >= criteria["volume_min"]]
        
        # Additional text-based filtering
        if criteria.get("keywords"):
            keywords = [k.lower() for k in criteria["keywords"]]
            filtered = [s for s in filtered if any(
                k in str(v).lower() 
                for k in keywords 
                for v in [s.get("name", ""), s.get("sector", ""), 
                         s.get("industry", ""), s.get("symbol", "")]
            )]
        
        return filtered

    def _sort_results(self, stocks: List[Dict], criteria: Dict) -> List[Dict]:
        """Sort results based on specified criteria"""
        sort_by = criteria.get("sort_by", "market_cap")
        sort_order = criteria.get("sort_order", "desc")
        
        def get_sort_value(stock: Dict) -> float:
            value = stock.get(sort_by, 0)
            return float(value if value is not None else 0)
        
        return sorted(
            stocks,
            key=get_sort_value,
            reverse=sort_order.lower() == "desc"
        )