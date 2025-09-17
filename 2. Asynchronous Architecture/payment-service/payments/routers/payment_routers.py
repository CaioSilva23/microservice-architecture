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
