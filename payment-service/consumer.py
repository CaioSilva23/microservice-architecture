import pika
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_to_rabbitmq(retries=5, delay=3):
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            channel = connection.channel()
            channel.queue_declare(queue="order_queue")
            logger.info("Conectado ao RabbitMQ com sucesso.")
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"[Tentativa {i+1}] Falha ao conectar ao RabbitMQ: {e}")
            time.sleep(delay)
    raise Exception("Não foi possível conectar ao RabbitMQ após várias tentativas.")


def callback(ch, method, properties, body):
    try:
        order = json.loads(body)
        logger.info(f"Atualizando estoque para o pedido: {order['product_id']}")
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")


def main():
    """Função principal para iniciar o consumidor RabbitMQ"""
    logger.info("Iniciando consumidor RabbitMQ...")

    channel = connect_to_rabbitmq()
    channel.basic_consume(queue="order_queue", on_message_callback=callback, auto_ack=True)
    logger.info("Esperando mensagens...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Interrompido manualmente. Encerrando consumidor.")


if __name__ == "__main__":
    main()
