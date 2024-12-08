from groq import OpenAI

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=Config.GROQ_API_KEY
        )
    
    async def process_query(self, query: str):
        system_prompt = """You are an expert at providing answers about stocks. 
        Please analyze the following query and extract relevant search criteria."""
        
        response = await self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content