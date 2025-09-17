import pika
import time
import json
import logging

# Configuração de logging
logger = logging.getLogger(__name__)


def publish_message(event: dict, retries=3, delay=2):
    """
    Publica um evento no RabbitMQ usando o exchange 'payment.process'.
    Inclui retry em caso de falha de conexão.
    """
    for attempt in range(retries):
        try:
            # Conexão com RabbitMQ
            conexao = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq')
            )
            canal = conexao.channel()

            # Declara o exchange do tipo fanout para broadcast
            canal.exchange_declare(exchange='payment.events', exchange_type='fanout', durable=True)

            # Não declaramos filas específicas - cada serviço cria a sua própria

            # Serializa o evento para JSON
            corpo_mensagem = json.dumps(event)

            # Publica a mensagem no exchange fanout (sem routing key)
            canal.basic_publish(
                exchange='payment.events',
                routing_key='',  # Fanout ignora routing_key
                body=corpo_mensagem,
                properties=pika.BasicProperties(
                    delivery_mode=2  # Faz a mensagem ser persistente
                )
            )

            logger.info(f"[x] Evento 'PaymentProcessed' enviado: {corpo_mensagem}")
            conexao.close()
            return True  # Sucesso, sair do loop

        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"Falha na conexão RabbitMQ (tentativa {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logger.error("Não foi possível publicar mensagem após todas as tentativas")
                raise
        except Exception as e:
            logger.error(f"Erro inesperado ao publicar mensagem: {e}")
            raise
