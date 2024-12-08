# src/services/llm_service.py
import groq
from src.config import Config

class LLMService:
    def __init__(self):
        self.client = groq.Groq(
            api_key=Config.GROQ_API_KEY
        )
    
    async def process_query(self, query: str):
        system_prompt = """You are an expert at providing answers about stocks. 
        Please analyze the following query and extract relevant search criteria."""
        
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                model="mixtral-8x7b-32768"
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error processing query: {str(e)}"