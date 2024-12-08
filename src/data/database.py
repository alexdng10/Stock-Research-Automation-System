# src/data/database.py
from sqlalchemy import create_engine, Column, String, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import Config

Base = declarative_base()

class StockData(Base):
    __tablename__ = "stocks"

    symbol = Column(String(10), primary_key=True)
    name = Column(String(255))
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)
    volume = Column(Integer)
    description = Column(Text)

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
        """
        Update or insert stock data in the database
        """
        session = self.SessionLocal()
        try:
            stock = StockData(**stock_data)
            session.merge(stock)  # merge will update if exists, insert if not
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    async def get_stock_data(self, symbol: str):
        """
        Retrieve stock data from database
        """
        session = self.SessionLocal()
        try:
            stock = session.query(StockData).filter(StockData.symbol == symbol).first()
            return stock
        finally:
            session.close() 