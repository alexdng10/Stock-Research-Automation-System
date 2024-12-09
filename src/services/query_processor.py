# src/services/query_processor.py

from src.services.llm_service import LLMService
from src.data.stock_client import StockClient
from typing import Dict, List, Any, Optional
import json
import logging
import re
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
        """Process natural language query and return relevant stock information."""
        try:
            logger.info(f"Processing query: {query}")

            # Handle direct stock symbol queries
            query_upper = query.strip().upper()
            if query_upper in self.stock_universe:
                stock_data = await self.stock_client.get_stock_details(query_upper)
                if "error" not in stock_data:
                    stock_info = self.stock_universe[query_upper]
                    stock_data.update({
                        "name": stock_info.name,
                        "sector": stock_info.sector,
                        "industry": stock_info.industry,
                    })
                    analyzed_stock = await self._analyze_stock(stock_data)
                    return {
                        "query": query,
                        "interpreted_as": f"Detailed analysis of {query_upper}",
                        "results_count": 1,
                        "results": [analyzed_stock],
                    }

            # Parse the query into structured data
            parsed_query = await self._parse_query(query)
            logger.debug(f"Parsed query: {parsed_query}")

            # Fetch stock data from static and live sources
            results = await self._fetch_stock_data()

            if not results:
                logger.warning("No stock data available at the moment.")
                return {
                    "query": query,
                    "error": "No stock data available",
                    "results": [],
                }

            # Apply filters to the fetched data
            filtered_results = self._apply_filters(results, parsed_query)

            # Apply analysis to **all filtered results**
            analyzed_results = [await self._analyze_stock(stock) for stock in filtered_results]

            # Sort the results if sorting criteria are specified
            if parsed_query.get("sort_by"):
                analyzed_results = self._sort_results(analyzed_results, parsed_query)

            response = {
                "query": query,
                "interpreted_as": parsed_query.get("description", ""),
                "results_count": len(analyzed_results),
                "results": analyzed_results[:10],  # Limit to top 10 results
            }

            logger.info(f"Query processed successfully with {len(analyzed_results)} results.")
            return response

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {"error": str(e), "query": query, "results": []}


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
    async def _analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single stock and provide insights."""
        try:
            prompt = (
                f"Analyze this stock data and provide key insights:\n"
                f"Symbol: {stock_data['symbol']}\n"
                f"Name: {stock_data.get('name', 'Unknown')}\n"
                f"Sector: {stock_data.get('sector', 'Unknown')}\n"
                f"Industry: {stock_data.get('industry', 'Unknown')}\n"
                f"Current Price: ${stock_data['current_price']}\n"
                f"Daily Change: {stock_data['daily_change_percent']}%\n"
                f"Market Cap: {stock_data['market_cap_formatted']}\n"
                f"Volume: {stock_data['volume']}\n"
                f"Day Range: ${stock_data['day_low']} - ${stock_data['day_high']}\n\n"
                "Return a JSON object with these fields:\n"
                "{\n"
                '  "performance_summary": "A concise analysis of today\'s performance including price movement and context",\n'
                '  "trading_volume_analysis": "Analysis of the trading volume and what it indicates",\n'
                '  "technical_signals": "Key technical indicators based on price position in day range",\n'
                '  "market_sentiment": "Overall market sentiment and recommendation",\n'
                '  "key_metrics": {\n'
                '    "price_strength": "strong|neutral|weak",\n'
                '    "volume_signal": "high|normal|low",\n'
                '    "trend": "bullish|bearish|neutral",\n'
                '    "volatility": "high|normal|low"\n'
                "  }\n"
                "}\n\n"
                "Keep each analysis field under 100 characters for concise display."
            )

            # Send the request to the LLM service
            response = await self.llm_service.process_query(prompt)

            # Log and validate response
            logger.debug(f"AI Response for {stock_data['symbol']}: {response}")

            if isinstance(response, str):
                response = json.loads(response)

            # Ensure response contains expected fields
            if not isinstance(response, dict) or "key_metrics" not in response:
                raise ValueError(f"Invalid AI response format for {stock_data['symbol']}: {response}")

            # Add analysis to stock data
            stock_data["analysis"] = {
                "performance_summary": response.get("performance_summary", "No data available"),
                "trading_volume_analysis": response.get("trading_volume_analysis", "No data available"),
                "technical_signals": response.get("technical_signals", "No data available"),
                "market_sentiment": response.get("market_sentiment", "No data available"),
                "key_metrics": {
                    "price_strength": response.get("key_metrics", {}).get("price_strength", "N/A"),
                    "volume_signal": response.get("key_metrics", {}).get("volume_signal", "N/A"),
                    "trend": response.get("key_metrics", {}).get("trend", "N/A"),
                    "volatility": response.get("key_metrics", {}).get("volatility", "N/A"),
                },
            }
            return stock_data

        except Exception as e:
            logger.error(f"Analysis failed for {stock_data['symbol']}: {e}")
            stock_data["analysis"] = {
                "performance_summary": "Analysis failed",
                "trading_volume_analysis": "Analysis failed",
                "technical_signals": "Analysis failed",
                "market_sentiment": "Analysis failed",
                "key_metrics": {
                    "price_strength": "N/A",
                    "volume_signal": "N/A",
                    "trend": "N/A",
                    "volatility": "N/A",
                },
            }
            return stock_data




    async def _parse_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured format with advanced fallback logic."""
        query_lower = query.lower()

        # Sector and industry keywords
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
            # Attempt advanced LLM parsing
            prompt = f"""
            Parse the following stock research query into structured JSON format:
            Query: {query}
            
            Fields to return:
            - sectors: list of relevant sectors
            - industries: list of relevant industries
            - market_cap_min: minimum market cap in billions (if mentioned)
            - market_cap_max: maximum market cap in billions (if mentioned)
            - volume_min: minimum trading volume (if mentioned)
            - keywords: list of key terms to match
            - sort_by: what to sort by (market_cap, volume, etc.)
            - sort_order: asc or desc
            - description: human-readable interpretation of the query
            """
            response = await self.llm_service.process_query(prompt)
            logger.debug(f"LLM parsed response: {response}")
            return json.loads(response) if isinstance(response, str) else response

        except Exception as e:
            logger.warning(f"LLM parsing failed. Falling back to static parsing: {str(e)}")

            # Fallback static parsing logic
            sectors = [sector_keywords[k] for k in sector_keywords if k in query_lower]
            industries = [industry_keywords[k] for k in industry_keywords if k in query_lower]

            # Extract possible keywords
            keywords = query_lower.split()

            # Default response with parsed components
            return {
                "sectors": sectors,
                "industries": industries,
                "keywords": keywords,
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