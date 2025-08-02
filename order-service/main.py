from fastapi import FastAPI
import uvicorn
from orders.routers.orders_routers import router
from shared.database import Base, engine
from shared.rebbitmq import connect_to_rabbitmq

# Importar os models para que o SQLAlchemy os reconheça
from orders.models.order import Order


def create_tables():
    """Cria tabelas e detecta mudanças na estrutura"""
    try:
        # Verificar conexão com o banco
        with engine.connect() as connection:
            print("🔗 Conexão com banco de dados estabelecida")
        
        from sqlalchemy import inspect, text
        inspector = inspect(engine)
        
        # Verificar se as tabelas existem
        existing_tables = inspector.get_table_names()
        print(f"📋 Tabelas existentes no banco: {existing_tables}")
        
        # Verificar estrutura da tabela orders se ela existir
        if 'orders' in existing_tables:
            print("🔍 Verificando estrutura da tabela 'orders'...")
            columns = inspector.get_columns('orders')
            existing_columns = [col['name'] for col in columns]
            print(f"📊 Colunas existentes: {existing_columns}")
            
            # Verificar se falta a coluna 'status'
            if 'status' not in existing_columns:
                print("⚠️  Detectada nova coluna 'status' - "
                      "Aplicando migração...")
                with engine.connect() as connection:
                    alter_sql = text(
                        "ALTER TABLE orders ADD COLUMN status VARCHAR(50) "
                        "NOT NULL DEFAULT 'PENDING'"
                    )
                    connection.execute(alter_sql)
                    connection.commit()
                print("✅ Coluna 'status' adicionada com sucesso!")
        
        # Criar/atualizar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas com sucesso!")
        
        # Listar estrutura final
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Tabelas finais disponíveis: {tables}")
        
        if 'orders' in tables:
            columns = inspector.get_columns('orders')
            final_columns = [col['name'] for col in columns]
            print(f"📊 Estrutura final da tabela 'orders': {final_columns}")
        
    except Exception as e:
        print(f"❌ Erro ao conectar/criar tabelas: {e}")
        print("💡 Verifique se o PostgreSQL está rodando e "
              "as credenciais no .env estão corretas")


def init_rabbitmq():
    """Inicializa a conexão com RabbitMQ"""
    try:
        print("🐰 Inicializando conexão com RabbitMQ...")
        connect_to_rabbitmq()
        print("✅ RabbitMQ configurado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar com RabbitMQ: {e}")
        print("💡 Verifique se o RabbitMQ está rodando")


def init_app():
    """Inicializa a aplicação FastAPI"""
    app = FastAPI(
        title="Projeto TCC API",
        description="API para gerenciamento de pedidos",
        version="1.0.0"
    )
    
    # Criar tabelas na inicialização
    create_tables()
    
    # Inicializar RabbitMQ
    init_rabbitmq()
    
    # Registrar routers
    app.include_router(router=router)
    
    return app


app = init_app()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
