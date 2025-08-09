from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    """
    Classe de resposta para notificações.
    Contém os atributos id e nome.
    """
    id: int
    pedido_id: int
    mensagem: str
    data_criacao: datetime
    status: str

    class Config:
        orm_mode = True
