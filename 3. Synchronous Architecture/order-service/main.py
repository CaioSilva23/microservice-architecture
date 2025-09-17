from fastapi import FastAPI, Response
import uvicorn
from orders.routers.orders_routers import router
from prometheus_client import (Counter, Histogram, generate_latest,
                               CONTENT_TYPE_LATEST)
import time

# from shared.database import Base, engine

# Importar os models para que o SQLAlchemy os reconheça
# from orders.models.order import Order


# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)

# Métricas do Prometheus
REQUEST_COUNT = Counter(
    'order_service_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'order_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)
ORDER_PROCESSED = Counter(
    'order_service_orders_processed_total',
    'Total orders processed',
    ['status']
)
RABBITMQ_MESSAGES = Counter(
    'order_service_rabbitmq_messages_total',
    'Total RabbitMQ messages',
    ['type', 'status']
)


def init_app():
    """Inicializa a aplicação FastAPI"""
    app = FastAPI(
        title="Projeto TCC API",
        description="API para gerenciamento de pedidos",
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

    # Registrar routers
    app.include_router(router=router)

    return app


app = init_app()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
