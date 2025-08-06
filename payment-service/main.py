from fastapi import FastAPI
import uvicorn
from payments.routers.payment_routers import router
from shared.consumer import process_payment_orders_creator_consumer
# from shared.database import Base, engine

# from payments.models.payment import Payment

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)


def init_process_payment_orders_creator_consumer():
    """Inicializa o consumidor de eventos de pedidos criados"""
    try:
        print("💳 Inicializando consumidor de eventos de pedidos criados...")
        process_payment_orders_creator_consumer()
        print("✅ Consumidor de pedidos criados iniciado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar consumidor de pedidos criados: {e}")
        print("💡 Verifique se o order-service está rodando")


def init_app():
    """Inicializa a aplicação FastAPI"""
    app = FastAPI(
        title="Projeto TCC API",
        description="API para gerenciamento de pagamentos",
        version="1.0.0"
    )

    # Inicializar consumidor de eventos de pedidos criados
    init_process_payment_orders_creator_consumer()

    # Registrar routers
    app.include_router(router=router)

    return app


app = init_app()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
