from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from shared.depedencies import get_db
from orders.models.order import Order
from orders.serializers import OrderRequest, OrderResponse


router = APIRouter(prefix="/orders", tags=["Orders"])


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

    event = {
            "event_type": "order_realized",
            "event_timestamp": datetime.now().isoformat(),
            "order_data": {
                "id": novo_pedido.id,
                "codigo": novo_pedido.codigo,
                "valor": str(novo_pedido.valor),
                "data": novo_pedido.data.isoformat(),
                "status": novo_pedido.status
            },
            "message": (
                f"Pedido {novo_pedido.codigo} foi realizado com sucesso"
            ),
            "metadata": {
                "service": "order-service",
                "version": "1.0.0"
            }
    }

    # enviar um post para o endpoint do notification-service e payment-service
    # dps precisa atualizar o status do pedido para "PAID" ou "PAYMENT_FAILED"
    return novo_pedido


@router.get(
    path="/{order_id}/status",
    summary="Verificar status do pedido",
    response_model=dict
)
def get_order_status(order_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Função para verificar o status de um pedido específico.
    Útil para acompanhar se o pagamento foi processado.
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return {
        "id": order.id,
        "codigo": order.codigo,
        "status": order.status,
        "valor": str(order.valor),
        "data": order.data.isoformat(),
        "status_description": {
            "PENDING": "Aguardando pagamento",
            "SUCCESS": "Pagamento confirmado",
            "PAYMENT_FAILED": "Falha no pagamento",
            "PAYMENT_PENDING": "Pagamento em processamento"
        }.get(order.status, "Status desconhecido")
    }


@router.patch(
    path="/{order_id}/status",
    summary="Atualizar status do pedido",
    response_model=dict
)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)) -> dict:
    """
    Função para atualizar o status de um pedido específico.
    """
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    order.status = status
    db.commit()

    return {
        "id": order.id,
        "codigo": order.codigo,
        "status": order.status,
        "valor": str(order.valor),
        "data": order.data.isoformat(),
        "status_description": {
            "PENDING": "Aguardando pagamento",
            "SUCCESS": "Pagamento confirmado",
            "PAYMENT_FAILED": "Falha no pagamento",
            "PAYMENT_PENDING": "Pagamento em processamento"
        }.get(order.status, "Status desconhecido")
    }


@router.get(
    path="/status/summary",
    summary="Resumo de status dos pedidos",
    response_model=dict
)
def get_orders_status_summary(db: Session = Depends(get_db)) -> dict:
    """
    Função para obter um resumo dos status de todos os pedidos.
    Útil para dashboard e monitoramento.
    """
    from sqlalchemy import func

    status_counts = db.query(
        Order.status,
        func.count(Order.id).label('count')
    ).group_by(Order.status).all()

    total_orders = db.query(func.count(Order.id)).scalar()

    return {
        "total_orders": total_orders,
        "status_breakdown": {
            status: count for status, count in status_counts
        },
        "status_descriptions": {
            "PENDING": "Aguardando pagamento",
            "PAID": "Pagamento confirmado",
            "PAYMENT_FAILED": "Falha no pagamento",
            "PAYMENT_PENDING": "Pagamento em processamento"
        }
    }
