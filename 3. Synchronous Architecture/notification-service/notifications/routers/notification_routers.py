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
from notifications.models.notification import Notification
from notifications.serializers.notifications import NotificationResponse

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# Modelo para requisição de envio síncrono
class NotificationSendRequest(BaseModel):
    order_id: int
    order_code: str
    message: str
    notification_type: str
    timestamp: str


# Modelo para resposta de envio síncrono
class NotificationSendResponse(BaseModel):
    success: bool
    notification_id: Optional[int] = None
    message: str
    processing_time_ms: float
    order_id: int


@router.post(
    "/send",
    summary="Enviar notificação síncronamente",
    response_model=NotificationSendResponse
)
def send_notification_sync(
    request: NotificationSendRequest,
    db: Session = Depends(get_db)
) -> NotificationSendResponse:
    """
    ENDPOINT SÍNCRONO - Envia notificação para arquitetura REST pura
    
    Este endpoint demonstra:
    - Processamento síncrono com latência controlada
    - Possibilidade de falhas que afetam o serviço solicitante
    - Acoplamento temporal entre serviços
    """
    start_time = time.time()
    
    logger.info(
        f"Enviando notificação síncrona para pedido {request.order_code}"
    )
    
    try:
        # Simular processamento de notificação (latência de rede/email)
        processing_delay = random.uniform(0.3, 1.5)  # 300ms a 1.5s
        time.sleep(processing_delay)
        
        # Simular falhas ocasionais (8% de chance)
        if random.random() < 0.08:
            logger.warning(
                f"Simulando falha no envio de notificação para pedido "
                f"{request.order_code}"
            )
            raise HTTPException(
                status_code=500,
                detail="Notification service temporarily unavailable"
            )
        
        # Criar registro de notificação enviada
        new_notification = Notification(
            message=request.message,
            notification_type=request.notification_type,
            order_id=request.order_id,
            status="SENT",
            sent_at=datetime.now()
        )
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(
            f"Notificação enviada para pedido {request.order_code} - "
            f"ID: {new_notification.id}"
        )
        
        return NotificationSendResponse(
            success=True,
            notification_id=new_notification.id,
            message=f"Notification sent for order {request.order_code}",
            processing_time_ms=processing_time,
            order_id=request.order_id
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        logger.error(
            f"Erro no envio de notificação para pedido "
            f"{request.order_code}: {e}"
        )
        
        # Em REST puro, erros se propagam diretamente
        raise HTTPException(
            status_code=500,
            detail=f"Notification sending failed: {str(e)}"
        )


@router.get("/listar", summary="List notifications")
def list_notifications(db: Session = Depends(get_db)) -> List[NotificationResponse]:
    """
    Função para listar notificações.
    Retorna uma lista de notificações.
    """
    notifications = db.query(Notification).all()
    return notifications
