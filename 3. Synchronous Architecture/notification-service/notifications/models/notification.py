from shared.database import Base
from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, nullable=False)
    message = Column(String(255), nullable=False)
    notification_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    sent_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
