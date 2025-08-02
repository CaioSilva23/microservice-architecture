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
        logger.info("Mensagem recebida!")

        order = json.loads(body)
        logger.info(f"Processando pedido: {order.get('codigo', 'N/A')}")

        # Simular processamento de pagamento
        logger.info("Pagamento processado com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")


def main():
    """Função principal para iniciar o consumidor RabbitMQ"""
    logger.info("=== INICIANDO PAYMENT SERVICE ===")

    logger.info("Conectando ao RabbitMQ...")
    channel = connect_to_rabbitmq()

    logger.info("Configurando consumidor da fila order_queue...")

    channel.basic_consume(
        queue="order_queue",
        on_message_callback=callback,
        auto_ack=True
    )

    logger.info("Aguardando mensagens... Pressione CTRL+C para sair")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Interrompido manualmente. Encerrando consumidor.")
        channel.stop_consuming()
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")


if __name__ == "__main__":
    main()
