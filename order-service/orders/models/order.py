from shared.database import Base
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(100), nullable=False)
    valor = Column(Numeric, nullable=False)
    data = Column(DateTime, nullable=False, default=datetime.now)
