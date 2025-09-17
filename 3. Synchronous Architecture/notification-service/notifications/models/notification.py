from shared.database import Base
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, nullable=False)
    mensagem = Column(String(255), nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)
    status = Column(String(50), nullable=False)
