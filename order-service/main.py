from fastapi import FastAPI
import uvicorn
from orders.routers.orders_routers import router
from shared.database import Base, engine

# Importar os models para que o SQLAlchemy os reconheça
from orders.models.order import Order


def create_tables():
    """Cria todas as tabelas no banco de dados"""
    try:
        # Verificar conexão com o banco
        with engine.connect() as connection:
            print("🔗 Conexão com banco de dados estabelecida")
        
        # Criar tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas com sucesso!")
        
        # Listar tabelas criadas
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tabelas disponíveis: {tables}")
        
    except Exception as e:
        print(f"❌ Erro ao conectar/criar tabelas: {e}")
        print("💡 Verifique se o PostgreSQL está rodando e as credenciais no .env estão corretas")


def init_app():
    """Inicializa a aplicação FastAPI"""
    app = FastAPI(
        title="Projeto TCC API",
        description="API para gerenciamento de pedidos",
        version="1.0.0"
    )
    
    # Criar tabelas na inicialização
    create_tables()
    
    # Registrar routers
    app.include_router(router=router)
    
    return app


app = init_app()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
