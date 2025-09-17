from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import datetime


class OrderResponse(BaseModel):
    """
    Classe de resposta para pedidos.
    Contém os atributos id e nome.
    """
    id: int
    codigo: str
    valor: Decimal
    data: datetime
    status: str

    class Config:
        orm_mode = True


class OrderRequest(BaseModel):
    """
    Classe de requisição para pedidos.
    Contém os atributos código, valor e data (opcional - usa data atual se não informada).
    """
    codigo: str
    valor: Decimal
    data: Optional[datetime] = None
