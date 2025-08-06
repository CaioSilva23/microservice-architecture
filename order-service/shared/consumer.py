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
            channel.queue_declare(queue='payment_queue', durable=True)

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

        # O payment-service envia tanto 'id' quanto 'codigo'
        # Vamos usar 'id' como order_id
        order_id = payment_event.get('id') or payment_event.get('codigo')
        payment_status = payment_event.get('status')

        if not order_id:
            logger.error("Evento de pagamento sem order_id/id/codigo")
            return

        # Mapear status de pagamento para status do pedido
        if payment_status == 'SUCCESS':
            new_status = 'SUCCESS'
        elif payment_status == 'FAILED':
            new_status = 'PAYMENT_FAILED'
        else:
            logger.warning(f"Status de pagamento desconhecido: {payment_status}")
            new_status = 'PAYMENT_PENDING'

        # Atualizar status do pedido
        time.sleep(3)  # Simular tempo de processamento
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
        retries = 5
        delay = 5
        
        for attempt in range(retries):
            try:
                logger.info(f"=== INICIANDO CONSUMIDOR DE EVENTOS DE PAGAMENTO (Tentativa {attempt + 1}/{retries}) ===")
                
                # Aguardar um pouco antes de tentar conectar
                if attempt > 0:
                    logger.info(f"Aguardando {delay} segundos antes de tentar novamente...")
                    time.sleep(delay)
                
                conexao = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
                canal = conexao.channel()

                logger.info("Configurando consumidor da fila payment_queue...")

                # Declara o mesmo exchange usado pelo produtor
                canal.exchange_declare(exchange='payment.process', exchange_type='direct', durable=True)

                # Usa a mesma fila que o produtor está publicando
                nome_fila = 'payment_queue'
                canal.queue_declare(queue=nome_fila, durable=True)

                # Liga a fila ao exchange com a mesma routing key vazia
                canal.queue_bind(exchange='payment.process', queue=nome_fila, routing_key='')

                logger.info(f"[🎧] Aguardando eventos 'PaymentProcessed' na fila {nome_fila}...")

                # Define o callback para processar mensagens com acknowledgment
                def callback_with_ack(ch, method, properties, body):
                    try:
                        payment_event_callback(ch, method, properties, body)
                        # Acknowledge da mensagem após processamento bem-sucedido
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    except Exception as e:
                        logger.error(f"Erro ao processar mensagem: {e}")
                        # Rejeita a mensagem e não recoloca na fila
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                canal.basic_consume(queue=nome_fila, on_message_callback=callback_with_ack)

                # Inicia o consumo
                logger.info("Consumidor conectado com sucesso! Iniciando consumo...")
                canal.start_consuming()
                break  # Se chegou aqui, a conexão foi bem-sucedida
                
            except pika.exceptions.AMQPConnectionError as e:
                logger.error(f"Erro de conexão com RabbitMQ (tentativa {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    logger.error("Não foi possível conectar ao RabbitMQ após todas as tentativas")
                    raise
            except Exception as e:
                logger.error(f"Erro inesperado no consumidor (tentativa {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise

    # Iniciar consumidor em thread separada para não bloquear a aplicação
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
    logger.info("Consumidor de eventos de pagamento iniciado em background")


# if __name__ == "__main__":
#     # Para teste isolado
#     start_payment_event_consumer()

#     # Manter o processo vivo
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         logger.info("Consumidor de pagamentos finalizado")
