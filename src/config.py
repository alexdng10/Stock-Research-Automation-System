from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock_research.db")
    
    # API Settings
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5"))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))