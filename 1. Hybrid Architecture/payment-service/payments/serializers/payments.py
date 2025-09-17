from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class PaymentResponse(BaseModel):
    """
    Classe de resposta para pagamentos.
    Contém os atributos id e nome.
    """
    id: int
    pedido_id: int
    valor: Decimal
    data_criacao: datetime
    status: str

    class Config:
        orm_mode = True
