from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from shared.depedencies import get_db
from notifications.models.notification import Notification
from notifications.serializers.notifications import NotificationResponse


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/listar", summary="List notifications")
def list_notifications(db: Session = Depends(get_db)) -> List[NotificationResponse]:
    """
    Função para listar notificações.
    Retorna uma lista de notificações.
    """
    notifications = db.query(Notification).all()
    return notifications
