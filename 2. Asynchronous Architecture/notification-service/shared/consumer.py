import pika
import json
import time
import logging
import sys
import threading
from sqlalchemy.orm import sessionmaker
from shared.database import engine
from notifications.models.notification import Notification


# Configuração de logging para Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# Criar sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_log_notification_event(order_id, status, mensagem):
    """Cria um log de evento de notificação"""
    logger.info(f"Salvando registro de notificação - Pedido ID: {order_id}, "
                f"Status: {status}, Mensagem: {mensagem}")

    db = SessionLocal()
    try:
        notification = Notification(
            pedido_id=order_id,
            status=status,
            mensagem=mensagem
        )
        db.add(notification)
        db.commit()
        logger.info(f"Registro de notificação salvo com sucesso - "
                    f"Pedido ID: {order_id}, Status: {status}")
    except Exception as e:
        logger.error(f"Erro ao salvar registro de notificação - "
                     f"Pedido ID: {order_id}, Status: {status}, Erro: {e}")
        db.rollback()
    finally:
        db.close()


def process_order_notification(ch, method, properties, body):
    """Processa notificações de eventos de pedidos criados"""
    evento = json.loads(body)
    logger.info(f"[✔] Evento de Pedido recebido: {evento}")

    # Simular o processamento (ex: iniciar notificação)
    payload = evento.get('order_data', {})

    pedido_codigo = payload.get("codigo")
    pedido_id = payload.get("id")
    status = payload.get("status")
    logger.info(f"→ Iniciando notificação para o pedido {pedido_codigo}")
    time.sleep(2)  # Simula o tempo de processamento

    # Salvar notificação no banco de dados
    create_log_notification_event(
        order_id=pedido_id,
        status=status,
        mensagem=f"Pedido {pedido_codigo} criado com status: {status}"
    )

    logger.info(f"[✔] Notificação de criação de pedido enviada para o "
                f"pedido {pedido_codigo}")

    # Confirma que a mensagem foi processada
    ch.basic_ack(delivery_tag=method.delivery_tag)


def process_payment_notification(ch, method, properties, body):
    """Processa notificações de eventos de pagamentos processados"""
    evento = json.loads(body)
    logger.info(f"[✔] Evento de Pagamento recebido: {evento}")

    # Extrair dados do evento de pagamento
    pedido_codigo = evento.get("codigo")
    pedido_id = evento.get("id")
    status = evento.get("status")
    valor = evento.get("valor")

    logger.info(f"→ Iniciando notificação de pagamento para o "
                f"pedido {pedido_codigo}")
    time.sleep(2)  # Simula o tempo de processamento

    # Determinar mensagem baseada no status do pagamento
    if status == "SUCCESS":
        mensagem = (f"Pagamento do pedido {pedido_codigo} foi processado "
                    f"com sucesso! Valor: R$ {valor}")
    elif status == "FAILED":
        mensagem = (f"Falha no pagamento do pedido {pedido_codigo}. "
                    f"Valor: R$ {valor}")
    else:
        mensagem = (f"Pagamento do pedido {pedido_codigo} está em "
                    f"processamento. Valor: R$ {valor}")

    # Salvar notificação no banco de dados
    create_log_notification_event(
        order_id=pedido_id,
        status=status,
        mensagem=mensagem
    )

    logger.info(f"[✔] Notificação de pagamento enviada para o "
                f"pedido {pedido_codigo}")

    # Confirma que a mensagem foi processada
    ch.basic_ack(delivery_tag=method.delivery_tag)


def process_notification_for_order():
    """Função principal para iniciar o consumidor de eventos de pedidos"""
    def consumer_thread():
        retries = 5
        delay = 5

        for attempt in range(retries):
            try:
                # Aguardar um pouco antes de tentar conectar
                if attempt > 0:
                    logger.info(f"Aguardando {delay} segundos antes de "
                                "tentar novamente...")
                    time.sleep(delay)

                logger.info(f"📝 Tentativa {attempt + 1}/{retries} de "
                            "conectar ao RabbitMQ para eventos de pedidos...")
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='rabbitmq')
                )
                channel = connection.channel()

                # Declara o exchange e a fila para eventos de pedidos
                channel.exchange_declare(
                    exchange='order.created',
                    exchange_type='fanout',
                    durable=True
                )

                queue_name = 'order_notification'
                channel.queue_declare(queue=queue_name, durable=True)
                channel.queue_bind(
                    exchange='order.created',
                    queue=queue_name
                )

                logger.info(f"[🎧] Aguardando eventos de pedidos na fila "
                            f"{queue_name}...")

                # Define o callback para processar mensagens
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=process_order_notification
                )

                # Inicia o consumo
                channel.start_consuming()
                break  # Se a conexão for bem-sucedida, sai do loop
            except Exception as e:
                logger.error(f"❌ Erro ao iniciar consumidor de pedidos: {e}")
                time.sleep(delay)

    # Iniciar consumidor em thread separada para não bloquear a aplicação
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
    logger.info("Consumidor de eventos de pedidos iniciado em background")


def process_notification_for_payment():
    """Função principal para iniciar o consumidor de eventos de pagamento"""
    def consumer_thread():
        retries = 5
        delay = 5

        for attempt in range(retries):
            try:
                # Aguardar um pouco antes de tentar conectar
                if attempt > 0:
                    logger.info(f"Aguardando {delay} segundos antes de "
                                "tentar novamente...")
                    time.sleep(delay)

                logger.info(f"💳 Tentativa {attempt + 1}/{retries} de "
                            "conectar ao RabbitMQ para eventos de pagamento...")
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host='rabbitmq')
                )
                channel = connection.channel()

                # Declara o exchange e a fila para eventos de pagamento
                channel.exchange_declare(
                    exchange='payment.events',
                    exchange_type='fanout',
                    durable=True
                )

                queue_name = 'payment_notification'
                channel.queue_declare(queue=queue_name, durable=True)
                channel.queue_bind(
                    exchange='payment.events',
                    queue=queue_name
                )

                logger.info(f"[🎧] Aguardando eventos de pagamento na fila "
                            f"{queue_name}...")

                # Define o callback para processar mensagens
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=process_payment_notification
                )

                # Inicia o consumo
                channel.start_consuming()
                break  # Se a conexão for bem-sucedida, sai do loop
            except Exception as e:
                logger.error(f"❌ Erro ao iniciar consumidor de "
                             f"pagamentos: {e}")
                time.sleep(delay)

    # Iniciar consumidor em thread separada para não bloquear a aplicação
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
    logger.info("Consumidor de eventos de pagamentos iniciado em background")
