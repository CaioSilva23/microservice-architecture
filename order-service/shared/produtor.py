import pika
import time
import json


def publish_message(event: dict):
    """Publica um evento no RabbitMQ usando o exchange 'order.created'.
    O evento é enviado como uma mensagem JSON.
    """

    # Conexão com RabbitMQ
    conexao = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    canal = conexao.channel()

    # Declara o exchange do tipo fanout (broadcast)
    canal.exchange_declare(exchange='order.created', exchange_type='fanout', durable=True)

    # Declarar fila
    canal.queue_declare(queue="order_queue")

    # Binding da fila ao exchange
    canal.queue_bind(
        exchange='order.created',
        queue='order_queue',
        routing_key=''
    )

    # Serializa o evento para JSON
    corpo_mensagem = json.dumps(event)

    # Publica a mensagem no exchange
    canal.basic_publish(
        exchange='order.created',
        routing_key='',  # Fanout ignora routing_key
        body=corpo_mensagem,
        properties=pika.BasicProperties(
            delivery_mode=2  # Faz a mensagem ser persistente
        )
    )
    print(f"[x] Evento 'OrderCreated' enviado: {corpo_mensagem}")
    conexao.close()
