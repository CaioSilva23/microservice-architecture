import pika
import json
import time
import logging
import sys

# Configuração de logging para Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def connect_to_rabbitmq(retries=5, delay=3, queue_name='order_queue'):
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            channel = connection.channel()
            
            # Declarar a fila principal (order_queue)
            channel.queue_declare(queue=queue_name)
            
            # Declarar o exchange FANOUT para distribuir pagamentos para múltiplos serviços
            channel.exchange_declare(
                exchange='payment_events',
                exchange_type='fanout',
                durable=True
            )
            
            # Declarar filas específicas para cada serviço
            # Fila para o order-service (atualizar status do pedido)
            channel.queue_declare(queue='order_payment_updates', durable=True)
            channel.queue_bind(
                exchange='payment_events',
                queue='order_payment_updates'
            )
            
            # Fila para o notification-service (enviar notificações)
            channel.queue_declare(queue='notification_payment_events', durable=True)
            channel.queue_bind(
                exchange='payment_events',
                queue='notification_payment_events'
            )
            
            logger.info(f"Conectado a fila {queue_name} com sucesso.")
            logger.info("Exchange 'payment_events' (fanout) configurado.")
            logger.info("Filas 'order_payment_updates' e 'notification_payment_events' criadas.")
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"[Tentativa {i+1}] Falha ao conectar a fila {queue_name}: {e}")
            time.sleep(delay)
    raise Exception(f"Não foi possível conectar a fila {queue_name} após várias tentativas.")


def publish_message(channel, exchange, body):
    """Publica uma mensagem no RabbitMQ usando fanout exchange"""
    try:
        channel.basic_publish(
            exchange=exchange,
            routing_key='',  # Fanout não usa routing_key
            body=json.dumps(body)
        )
        logger.info(f"Evento de pagamento publicado para todos os serviços: {body}")
    except Exception as e:
        logger.error(f"Erro ao publicar mensagem: {e}")


def callback(ch, method, properties, body):
    time.sleep(3)  # Simular processamento lento
    try:
        logger.info("Mensagem recebida!")

        order = json.loads(body)
        logger.info(f"Processando pedido: {order.get('codigo', 'N/A')}")

        # Preparar evento de pagamento para múltiplos serviços
        payment_event = {
            "payment_id": f"pay_{order.get('id', 'unknown')}",
            "order_id": order.get('id'),
            "order_code": order.get('codigo'),
            "status": "success",
            "amount": order.get('valor', 0),
            "timestamp": time.time(),
            "event_type": "payment_processed"
        }

        # Publicar evento para todos os serviços interessados
        publish_message(
            channel=ch,
            exchange='payment_events',
            body=payment_event
        )

        logger.info("Pagamento processado com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")


def main():
    """Função principal para iniciar o consumidor RabbitMQ"""
    logger.info("=== INICIANDO PAYMENT SERVICE ===")

    logger.info("Conectando ao RabbitMQ...")
    channel = connect_to_rabbitmq(queue_name="order_queue")

    logger.info("Configurando consumidor da fila order_queue...")

    channel.basic_consume(
        queue="order_queue",
        on_message_callback=callback,
        auto_ack=True
    )

    logger.info("Aguardando mensagens... ")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Interrompido manualmente. Encerrando consumidor.")
        channel.stop_consuming()
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")


if __name__ == "__main__":
    main()
