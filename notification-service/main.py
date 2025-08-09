from fastapi import FastAPI
import uvicorn
from notifications.routers.notification_routers import router
from shared.consumer import (
    process_notification_for_order,
    process_notification_for_payment
)

# from shared.database import Base, engine
# from notifications.models.notification import Notification

# Base.metadata.drop_all(bind=engine)
# Base.metadata.create_all(bind=engine)


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
