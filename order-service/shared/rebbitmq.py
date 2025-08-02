import pika
import time
import json


def connect_to_rabbitmq(retries=5, delay=3):
    for i in range(retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            channel = connection.channel()
            
            # Declarar exchange
            channel.exchange_declare(
                exchange='orders',
                exchange_type='topic'
            )
            
            # Declarar fila
            channel.queue_declare(queue="order_queue")
            
            # Binding da fila ao exchange
            channel.queue_bind(
                exchange='orders',
                queue='order_queue',
                routing_key='order.*'
            )
            
            print("Conectado ao RabbitMQ com sucesso.")
            return channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"[Tentativa {i+1}] Falha ao conectar ao RabbitMQ: {e}")
            time.sleep(delay)
    raise Exception(
        "Não foi possível conectar ao RabbitMQ após várias tentativas."
    )


# Conectar no startup do app
channel = connect_to_rabbitmq()


def publish_message(exchange, routing_key, body):
    global channel
    try:
        # Verificar se o canal ainda está aberto
        if channel.is_closed:
            print("Canal fechado, reconectando...")
            channel = connect_to_rabbitmq()
        
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(body)
        )
        print(f"Mensagem publicada: {body}")
    except pika.exceptions.AMQPError as e:
        print(f"Erro ao publicar mensagem: {e}")
        # Tentar reconectar e publicar novamente
        try:
            channel = connect_to_rabbitmq()
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(body)
            )
            print(f"Mensagem publicada após reconexão: {body}")
        except Exception as reconnect_error:
            print(f"Falha ao reconectar e publicar: {reconnect_error}")
