from shared.database import Base
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)
    status = Column(String(50), nullable=False)
