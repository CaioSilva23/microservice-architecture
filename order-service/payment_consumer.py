import pika
import json
import time
import logging
import threading
from sqlalchemy.orm import sessionmaker
from shared.database import engine
from orders.models.order import Order

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def connect_to_payment_events(retries=5, delay=3):
    """Conecta ao RabbitMQ para ouvir eventos de pagamento"""
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            channel = connection.channel()
            
            # Verificar se a fila existe (criada pelo payment-service)
            channel.queue_declare(queue='order_payment_updates', durable=True)
            
            logger.info("Conectado à fila de eventos de pagamento com sucesso.")
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"[Tentativa {i+1}] Falha ao conectar: {e}")
            time.sleep(delay)
    raise Exception("Não foi possível conectar ao RabbitMQ para eventos de pagamento.")


def update_order_status(order_id: int, new_status: str):
    """Atualiza o status do pedido no banco de dados"""
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            old_status = order.status
            order.status = new_status
            db.commit()
            logger.info(f"Pedido {order_id} atualizado: {old_status} -> {new_status}")
            return True
        else:
            logger.warning(f"Pedido {order_id} não encontrado no banco de dados")
            return False
    except Exception as e:
        logger.error(f"Erro ao atualizar pedido {order_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def payment_event_callback(ch, method, properties, body):
    """Processa eventos de pagamento recebidos"""
    try:
        payment_event = json.loads(body)
        logger.info(f"Evento de pagamento recebido: {payment_event}")
        
        order_id = payment_event.get('order_id')
        payment_status = payment_event.get('status')
        
        if not order_id:
            logger.error("Evento de pagamento sem order_id")
            return
        
        # Mapear status de pagamento para status do pedido
        if payment_status == 'success':
            new_status = 'SUCCESS'
        elif payment_status == 'failed':
            new_status = 'PAYMENT_FAILED'
        else:
            logger.warning(f"Status de pagamento desconhecido: {payment_status}")
            new_status = 'PAYMENT_PENDING'
        
        # Atualizar status do pedido
        success = update_order_status(order_id, new_status)
        
        if success:
            logger.info(f"Pedido {order_id} processado com sucesso - Status: {new_status}")
        else:
            logger.error(f"Falha ao processar pedido {order_id}")
            
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        logger.error(f"Erro ao processar evento de pagamento: {e}")


def start_payment_event_consumer():
    """Inicia o consumidor de eventos de pagamento em uma thread separada"""
    def consumer_thread():
        try:
            logger.info("=== INICIANDO CONSUMIDOR DE EVENTOS DE PAGAMENTO ===")
            
            channel = connect_to_payment_events()
            
            channel.basic_consume(
                queue='order_payment_updates',
                on_message_callback=payment_event_callback,
                auto_ack=True
            )
            
            logger.info("Aguardando eventos de pagamento...")
            channel.start_consuming()
            
        except Exception as e:
            logger.error(f"Erro no consumidor de eventos de pagamento: {e}")
    
    # Iniciar consumidor em thread separada para não bloquear a aplicação
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
    logger.info("Consumidor de eventos de pagamento iniciado em background")


if __name__ == "__main__":
    # Para teste isolado
    start_payment_event_consumer()
    
    # Manter o processo vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Consumidor de pagamentos finalizado")
