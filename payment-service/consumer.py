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
            
            # Declarar a fila
            channel.queue_declare(queue=queue_name)
            
            # Declarar o exchange para pagamentos
            channel.exchange_declare(
                exchange='payments',
                exchange_type='direct',
                durable=True
            )
            
            # Declarar a fila de pagamentos e fazer o bind
            channel.queue_declare(queue='payment_queue', durable=True)
            channel.queue_bind(
                exchange='payments',
                queue='payment_queue',
                routing_key='payment.created'
            )
            
            logger.info(f"Conectado a fila {queue_name} com sucesso.")
            logger.info("Exchange 'payments' e fila 'payment_queue' configurados.")
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"[Tentativa {i+1}] Falha ao conectar a fila {queue_name}: {e}")
            time.sleep(delay)
    raise Exception(f"Não foi possível conectar a fila {queue_name} após várias tentativas.")


def publish_message(channel, exchange, routing_key, body):
    """Publica uma mensagem no RabbitMQ usando o canal existente"""
    try:
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(body)
        )
        logger.info(f"Mensagem publicada: {body}")
    except Exception as e:
        logger.error(f"Erro ao publicar mensagem: {e}")


def callback(ch, method, properties, body):
    time.sleep(3)  # Simular processamento lento
    try:
        logger.info("Mensagem recebida!")

        order = json.loads(body)
        logger.info(f"Processando pedido: {order.get('codigo', 'N/A')}")

        publish_message(
            channel=ch,
            exchange='payments',
            routing_key='payment.created',
            body={
                "id": order.get('id'),
                "status": "success",
            }
        )

        # Simular processamento de pagamento
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
