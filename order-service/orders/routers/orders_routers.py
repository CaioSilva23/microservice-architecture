from fastapi import APIRouter, Depends
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from shared.depedencies import get_db
from orders.models.order import Order


router = APIRouter(prefix="/orders", tags=["Orders"])


class OrderResponse(BaseModel):
    """
    Classe de resposta para pedidos.
    Contém os atributos id e nome.
    """
    id: int
    codigo: str
    valor: Decimal
    data: datetime

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


@router.get("/listar", summary="List orders")
def list_orders(db: Session = Depends(get_db)) -> List[OrderResponse]:
    """
    Função para listar pedidos.
    Retorna uma lista de pedidos.
    """
    orders = db.query(Order).all()
    return orders


@router.post(
        path="/criar",
        summary="Criar pedido",
        response_model=OrderResponse,
        status_code=201
)
def criar_pedido(pedido: OrderRequest, db: Session = Depends(get_db)) -> OrderResponse:
    """
    Função para criar um novo pedido.
    Se a data não for fornecida, usa a data/hora atual.
    Retorna o pedido criado.
    """
    
    # Preparar dados do pedido
    pedido_data = pedido.model_dump()
    
    # Se data não foi fornecida, usar data atual
    if pedido_data['data'] is None:
        pedido_data['data'] = datetime.now()

    novo_pedido = Order(**pedido_data)
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    return novo_pedido
