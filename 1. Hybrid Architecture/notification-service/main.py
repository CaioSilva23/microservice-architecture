from fastapi import FastAPI, Response
import uvicorn
from notifications.routers.notification_routers import router
from shared.consumer import (
    process_notification_for_order,
    process_notification_for_payment
)
from prometheus_client import (Counter, Histogram, generate_latest,
                               CONTENT_TYPE_LATEST)
import time

# from shared.database import Base, engine
# from notifications.models.notification import Notification

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

# Métricas do Prometheus
REQUEST_COUNT = Counter(
    'notification_service_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'notification_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)
NOTIFICATION_PROCESSED = Counter(
    'notification_service_notifications_processed_total',
    'Total notifications processed',
    ['type', 'status']
)
RABBITMQ_MESSAGES = Counter(
    'notification_service_rabbitmq_messages_total',
    'Total RabbitMQ messages',
    ['type', 'status']
)


def init_process_notification_for_order():
    """Inicializa o consumidor de eventos de pedidos"""
    try:
        print("� Inicializando consumidor de eventos de pedidos")
        process_notification_for_order()
        print("✅ Consumidor de pedidos iniciado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar consumidor de pedidos: {e}")
        print("💡 Verifique se o order-service está rodando")


def init_process_notification_for_payment():
    """Inicializa o consumidor de eventos de pagamentos"""
    try:
        print("💳 Inicializando consumidor de eventos de pagamentos")
        process_notification_for_payment()
        print("✅ Consumidor de pagamentos iniciado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar consumidor de pagamentos: {e}")
        print("💡 Verifique se o payment-service está rodando")


def init_app():
    """Inicializa a aplicação FastAPI"""
    app = FastAPI(
        title="Notification API",
        description="API para gerenciamento de notificações de status de "
                    "pedidos e pagamentos",
        version="1.0.0"
    )

    # Middleware para instrumentação de métricas
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

    # Endpoint para métricas do Prometheus
    @app.get("/metrics")
    async def metrics():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )

    # Inicializar consumidores de eventos
    init_process_notification_for_order()
    init_process_notification_for_payment()

    # Registrar routers
    app.include_router(router=router)

    return app


app = init_app()


@app.get("/")
async def root() -> dict:
    return {"message": "Notification Service - Ouvindo eventos de pedidos "
                       "e pagamentos"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
