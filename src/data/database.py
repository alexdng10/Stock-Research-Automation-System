# src/data/database.py

from sqlalchemy import create_engine, Column, String, Float, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from src.config import Config

Base = declarative_base()

class StockData(Base):
    __tablename__ = "stocks"

    symbol = Column(String(10), primary_key=True)
    name = Column(String(255))
    current_price = Column(Float)
    volume = Column(Integer)
    day_high = Column(Float)
    day_low = Column(Float)
    day_open = Column(Float)
    market_cap = Column(Float)
    sector = Column(String(100))
    industry = Column(String(100))
    description = Column(Text)
    daily_change = Column(Float)
    daily_change_percent = Column(Float)

class Database:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    async def update_stock_data(self, stock_data: dict):
        """Update or insert stock data in the database"""
        session = self.SessionLocal()
        try:
            # Filter out any keys that don't exist in the model
            valid_keys = [column.key for column in StockData.__table__.columns]
            filtered_data = {k: v for k, v in stock_data.items() if k in valid_keys}
            
            stock = StockData(**filtered_data)
            session.merge(stock)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()