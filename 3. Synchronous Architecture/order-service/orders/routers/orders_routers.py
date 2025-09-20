from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import httpx
import logging
from shared.depedencies import get_db
from orders.models.order import Order
from orders.serializers import OrderRequest, OrderResponse

# Configurar logging
logger = logging.getLogger(__name__)

# URLs dos serviços (via service discovery do Docker)
PAYMENT_SERVICE_URL = "http://payment-service:8001"
NOTIFICATION_SERVICE_URL = "http://notification-service:8002"

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
    ARQUITETURA REST PURA (SÍNCRONA) - Criar novo pedido
    
    Esta implementação demonstra o padrão síncrono puro:
    1. SÍNCRONO: Persistência no banco
    2. SÍNCRONO: Comunicação com outros serviços via HTTP (quando implementado)
    
    Características:
    - Menor latência (comunicação direta)
    - Acoplamento temporal (dependências diretas)
    - Vulnerável a falhas em cascata
    - Simplicidade de implementação e debugging
    
    Nota: Para comunicação real com payment/notification services,
    seriam feitas chamadas HTTP síncronas adicionais aqui.
    """

    # ===== OPERAÇÃO SÍNCRONA ÚNICA =====
    # Preparar dados do pedido
    pedido_data = pedido.model_dump()

    # Se data não foi fornecida, usar data atual
    if pedido_data['data'] is None:
        pedido_data['data'] = datetime.now()

    novo_pedido = Order(**pedido_data)
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    # ===== COMUNICAÇÕES HTTP SÍNCRONAS (DEMONSTRAÇÃO REST PURA) =====
    # IMPORTANTE: Estas chamadas são BLOQUEANTES e podem causar falhas em cascata
    
    payment_success = False
    notification_success = False
    
    try:
        # 1. CHAMADA SÍNCRONA PARA PAYMENT SERVICE (CRÍTICA)
        logger.info(f"Iniciando pagamento síncrono para pedido {novo_pedido.codigo}")
        
        payment_data = {
            "order_id": novo_pedido.id,
            "order_code": novo_pedido.codigo,
            "amount": float(novo_pedido.valor),
            "timestamp": datetime.now().isoformat()
        }
        
        with httpx.Client(timeout=10.0) as client:
            payment_response = client.post(
                f"{PAYMENT_SERVICE_URL}/payments/process",
                json=payment_data
            )
            
            if payment_response.status_code == 200:
                payment_result = payment_response.json()
                payment_success = payment_result.get("success", False)
                
                # Atualizar status do pedido baseado no pagamento
                if payment_success:
                    novo_pedido.status = "PAYMENT_SUCCESS"
                    logger.info(f"Pagamento aprovado para pedido {novo_pedido.codigo}")
                else:
                    novo_pedido.status = "PAYMENT_FAILED"
                    logger.warning(f"Pagamento rejeitado para pedido {novo_pedido.codigo}")
            else:
                novo_pedido.status = "PAYMENT_FAILED"
                logger.error(f"Erro na comunicação com payment service: {payment_response.status_code}")
                
    except httpx.TimeoutException:
        novo_pedido.status = "PAYMENT_TIMEOUT"
        logger.error(f"Timeout na comunicação com payment service para pedido {novo_pedido.codigo}")
        # PROBLEMA: Em REST puro, timeout afeta toda a operação
        
    except httpx.RequestError as e:
        novo_pedido.status = "PAYMENT_ERROR"
        logger.error(f"Erro na requisição para payment service: {e}")
        # PROBLEMA: Falha no payment service causa falha na criação do pedido
    
    try:
        # 2. CHAMADA SÍNCRONA PARA NOTIFICATION SERVICE (NÃO-CRÍTICA)
        logger.info(f"Enviando notificação síncrona para pedido {novo_pedido.codigo}")
        
        notification_data = {
            "order_id": novo_pedido.id,
            "order_code": novo_pedido.codigo,
            "status": novo_pedido.status,
            "message": f"Pedido {novo_pedido.codigo} - Status: {novo_pedido.status}",
            "timestamp": datetime.now().isoformat()
        }
        
        with httpx.Client(timeout=5.0) as client:
            notification_response = client.post(
                f"{NOTIFICATION_SERVICE_URL}/notifications/send",
                json=notification_data
            )
            
            if notification_response.status_code == 200:
                notification_success = True
                logger.info(f"Notificação enviada para pedido {novo_pedido.codigo}")
            else:
                logger.error(f"Erro na comunicação com notification service: {notification_response.status_code}")
                
    except (httpx.TimeoutException, httpx.RequestError) as e:
        logger.error(f"Erro na notificação para pedido {novo_pedido.codigo}: {e}")
        # NOTA: Falha na notificação não deveria comprometer o pedido,
        # mas em REST puro isso pode afetar a experiência do usuário
    
    # Salvar atualizações finais
    db.commit()
    db.refresh(novo_pedido)
    
    # ===== RESPOSTA COM INFORMAÇÕES DE DEBUG =====
    logger.info(f"Pedido {novo_pedido.codigo} criado - Payment: {payment_success}, Notification: {notification_success}")
    
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
