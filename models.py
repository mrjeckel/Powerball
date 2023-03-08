from sqlalchemy import Column, Date, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class WinningNumbers(Base):
    __tablename__ = "WinningNumbers"

    date = Column(Date, primary_key=True)
    numbers = Column(Text, nullable=False)
