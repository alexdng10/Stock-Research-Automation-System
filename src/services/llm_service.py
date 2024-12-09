import groq
from src.config import Config
import asyncio
import json
import re

class LLMService:
    def __init__(self):
        self.client = groq.Groq(
            api_key=Config.GROQ_API_KEY
        )

    async def process_query(self, query: str):
        if "Analyze this stock data" in query:
            # This is a stock analysis request
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a stock market expert. Analyze the given stock data and provide insights.
                        Return a JSON object with these exact fields:
                        {
                            "performance_summary": "brief analysis of performance",
                            "trading_volume_analysis": "volume analysis",
                            "technical_signals": "technical analysis",
                            "market_sentiment": "overall sentiment",
                            "key_metrics": {
                                "price_strength": "strong|neutral|weak",
                                "volume_signal": "high|normal|low",
                                "trend": "bullish|bearish|neutral",
                                "volatility": "high|normal|low"
                            }
                        }"""
                    },
                    {"role": "user", "content": query}
                ]
            )
        else:
            # This is a search criteria request
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": """Extract search criteria from the query.
                        Return a JSON object with these exact fields:
                        {
                            "sectors": ["list of sectors"],
                            "industries": ["list of industries"],
                            "market_cap_min": null,
                            "market_cap_max": null,
                            "keywords": ["key terms"],
                            "description": "human readable interpretation"
                        }"""
                    },
                    {"role": "user", "content": query}
                ]
            )

        response = completion.choices[0].message.content.strip()
        
        try:
            # Try to parse as JSON directly
            return json.loads(response)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON object
            matches = re.findall(r'\{.*\}', response, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches[0])
                except:
                    pass
            
            # If all parsing fails, return error response
            return {
                "error": "Failed to parse LLM response",
                "raw_response": response
            }
