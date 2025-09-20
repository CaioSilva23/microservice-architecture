from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import random
import time
import logging
from shared.depedencies import get_db
from payments.models.payment import Payment
from payments.serializers.payments import PaymentResponse

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


# Modelo para requisição de processamento síncrono
class PaymentProcessRequest(BaseModel):
    order_id: int
    order_code: str
    amount: float
    timestamp: str


# Modelo para resposta de processamento síncrono
class PaymentProcessResponse(BaseModel):
    success: bool
    payment_id: Optional[int] = None
    message: str
    processing_time_ms: float
    order_id: int


@router.post(
    "/process",
    summary="Processar pagamento síncronamente",
    response_model=PaymentProcessResponse
)
def process_payment_sync(
    request: PaymentProcessRequest,
    db: Session = Depends(get_db)
) -> PaymentProcessResponse:
    """
    ENDPOINT SÍNCRONO - Processa pagamento para arquitetura REST pura
    
    Este endpoint demonstra:
    - Processamento síncrono com latência controlada
    - Possibilidade de falhas que afetam o serviço solicitante
    - Acoplamento temporal entre Order Service e Payment Service
    """
    start_time = time.time()
    
    logger.info(
        f"Processando pagamento síncrono para pedido {request.order_code}"
    )
    
    try:
        # Simular processamento de pagamento (latência realística)
        processing_delay = random.uniform(0.5, 2.0)  # 500ms a 2s
        time.sleep(processing_delay)
        
        # Simular falhas ocasionais (10% de chance)
        if random.random() < 0.1:
            logger.warning(
                f"Simulando falha no pagamento para pedido {request.order_code}"
            )
            raise HTTPException(
                status_code=500,
                detail="Payment service temporarily unavailable"
            )
        
        # Simular rejeição de pagamento (5% de chance)
        payment_approved = random.random() > 0.05
        
        if payment_approved:
            # Criar registro de pagamento aprovado
            new_payment = Payment(
                amount=Decimal(str(request.amount)),
                order_id=request.order_id,
                status="SUCCESS",
                processed_at=datetime.now()
            )
            db.add(new_payment)
            db.commit()
            db.refresh(new_payment)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"Pagamento aprovado para pedido {request.order_code} - "
                f"ID: {new_payment.id}"
            )
            
            return PaymentProcessResponse(
                success=True,
                payment_id=new_payment.id,
                message=f"Payment approved for order {request.order_code}",
                processing_time_ms=processing_time,
                order_id=request.order_id
            )
        else:
            # Pagamento rejeitado (mas sem erro de sistema)
            processing_time = (time.time() - start_time) * 1000
            
            logger.warning(
                f"Pagamento rejeitado para pedido {request.order_code}"
            )
            
            return PaymentProcessResponse(
                success=False,
                payment_id=None,
                message=f"Payment declined for order {request.order_code}",
                processing_time_ms=processing_time,
                order_id=request.order_id
            )
            
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(
            f"Erro no processamento de pagamento para pedido "
            f"{request.order_code}: {e}"
        )
        
        # Em REST puro, erros se propagam diretamente
        raise HTTPException(
            status_code=500,
            detail=f"Payment processing failed: {str(e)}"
        )


@router.get("/listar", summary="List payments")
def list_payments(db: Session = Depends(get_db)) -> List[PaymentResponse]:
    """
    Função para listar pagamentos.
    Retorna uma lista de pagamentos.
    """
    payments = db.query(Payment).all()
    return payments


@router.post(
    path="/processar",
    summary="Processar pagamento",
    response_model=PaymentResponse,
    status_code=201
)
def process_payment(amount: Decimal, order_id: int, db: Session = Depends(get_db)) -> PaymentResponse:
    """
    Função para processar um pagamento.
    Retorna o pagamento processado.
    """

    # Simular processamento de pagamento
    new_payment = Payment(
        amount=amount,
        order_id=order_id,
        status="processed",
        processed_at=datetime.now()
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Enviar um post para o endpoint do notification-service
    event = {
            "event_type": "payment_processed",
            "event_timestamp": datetime.now().isoformat(),
            "payment_data": {
                "id": new_payment.id,
                "amount": str(new_payment.amount),
                "order_id": new_payment.order_id,
                "status": new_payment.status,
                "processed_at": new_payment.processed_at.isoformat()
            },
            "message": (
                f"Pagamento processado para o pedido {new_payment.order_id} "
                f"no valor de {new_payment.amount}"
            )
    }
    # enviar um post para o endpoint do notification-service
    # requests.post("http://notification-service/notifications/create", json=event) --- IGN

    return new_payment
