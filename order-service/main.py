from fastapi import FastAPI
import uvicorn
from orders.routers.orders_routers import router
from shared.consumer import start_payment_event_consumer

# from shared.database import Base, engine

# Importar os models para que o SQLAlchemy os reconheça
# from orders.models.order import Order


# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)


def init_payment_consumer():
    """Inicializa o consumidor de eventos de pagamento"""
    try:
        print("💳 Inicializando consumidor de eventos de pagamento...")
        start_payment_event_consumer()
        print("✅ Consumidor de pagamentos iniciado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar consumidor de pagamentos: {e}")
        print("💡 Verifique se o payment-service está rodando")


def init_app():
    """Inicializa a aplicação FastAPI"""
    app = FastAPI(
        title="Projeto TCC API",
        description="API para gerenciamento de pedidos",
        version="1.0.0"
    )

    # Inicializar consumidor de eventos de pagamento
    init_payment_consumer()

    # Registrar routers
    app.include_router(router=router)

    return app


app = init_app()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
