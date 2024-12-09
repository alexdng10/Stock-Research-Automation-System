import groq
from src.config import Config
import asyncio

class LLMService:
    def __init__(self):
        self.client = groq.Groq(
            api_key=Config.GROQ_API_KEY
        )

    async def process_query(self, query: str):
        system_prompt = """You are an expert at providing answers about stocks. 
        Please analyze the following query and extract relevant search criteria.
        Return the response in this JSON format:
        {
            "sector": "optional sector to filter by",
            "market_cap_min": "optional minimum market cap",
            "keywords": ["list", "of", "keywords"],
            "description": "human readable interpretation of the query"
        }
        """
        
        try:
            # Ensure the API call supports async or run it in a separate thread if sync
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            )
            
            # Return the content from the response
            return completion.choices[0].message.content
        
        except Exception as e:
            # Log and return a fallback response in case of an error
            return {
                "error": f"Error processing query: {str(e)}",
                "keywords": query.lower().split(),
                "description": "Failed to process query with LLM, using basic keyword search"
            }
