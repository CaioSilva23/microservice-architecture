import pika
import json
import time
import logging
import sys
from produtor import publish_message


# Configuração de logging para Docker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def process_payment(ch, method, properties, body):
    evento = json.loads(body)
    logger.info(f"[✔] PedidoCriado recebido: {evento}")

    # Simular o processamento (ex: iniciar pagamento)
    payload = evento.get('order_data', {})

    pedido_id = payload.get("codigo")
    logger.info(f"→ Iniciando processamento de pagamento para o pedido {pedido_id}")
    time.sleep(5)  # Simula o tempo de processamento

    publish_message({
        "evento": "PaymentProcessed",
        "codigo": pedido_id,
        "id": payload.get("id"),
        "valor": payload.get("valor"),
        "status": "SUCCESS",
        "data": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "metadata": {
            "source": "payment-service",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        }
    })

    logger.info(f"[✔] Pagamento processado com sucesso para o pedido {pedido_id}")

    # Confirma que a mensagem foi processada
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """Função principal para iniciar o consumidor RabbitMQ"""
    logger.info("=== INICIANDO PAYMENT SERVICE ===")

    logger.info("Conectando ao RabbitMQ...")
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    canal = conexao.channel()

    logger.info("Configurando consumidor da fila order_queue...")

    # Declara o mesmo exchange usado pelo produtor
    canal.exchange_declare(exchange='order.created', exchange_type='fanout', durable=True)

    # Declara a fila (pode ser uma por serviço)
    nome_fila = 'order_payment'
    canal.queue_declare(queue=nome_fila, durable=True)

    # Liga a fila ao exchange
    canal.queue_bind(exchange='order.created', queue=nome_fila)

    logger.info(f"[🎧] Aguardando eventos 'PedidoCriado' na fila {nome_fila}...")

    # Define o callback para processar mensagens
    canal.basic_consume(queue=nome_fila, on_message_callback=process_payment)

    # Inicia o consumo
    canal.start_consuming()


if __name__ == "__main__":
    main()
