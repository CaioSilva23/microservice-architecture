from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from shared.depedencies import get_db
from payments.models.payment import Payment
from payments.serializers.payments import PaymentResponse


router = APIRouter(prefix="/payments", tags=["Payments"])


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
