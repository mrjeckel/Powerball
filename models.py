from sqlalchemy import Column, Date, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LotteryDraw(Base):
    __tablename__ = "LotteryDraw"

    date = Column(Date, primary_key=True)
    numbers = Column(Text, nullable=False)
    single = Column(Text, nullable=False)
