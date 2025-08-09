import pika
import json
import time
import logging
import sys
from shared.produtor import publish_message
import threading
from sqlalchemy.orm import sessionmaker
from shared.database import engine
from payments.models.payment import Payment


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


def create_log_payment_event(order_id, status, valor):
    """Cria um log de evento de pagamento"""
    logger.info(f"Salvando registro de pagamento - Pedido ID: {order_id}, Status: {status}, Valor: {valor}")
    # Aqui você pode adicionar a lógica para salvar o pagamento no banco de dados

    db = SessionLocal()
    try:
        payment = Payment(pedido_id=order_id, status=status, valor=valor)
        db.add(payment)
        db.commit()
        logger.info(f"Registro de pagamento salvo com sucesso - Pedido ID: {order_id}, Status: {status}, Valor: {valor}")
    except Exception as e:
        logger.error(f"Erro ao salvar registro de pagamento - Pedido ID: {order_id}, Status: {status}, Valor: {valor}, Erro: {e}")
        db.rollback()
    finally:
        db.close()


def process_payment(ch, method, properties, body):
    evento = json.loads(body)
    logger.info(f"[✔] PedidoCriado recebido: {evento}")

    # Simular o processamento (ex: iniciar pagamento)
    payload = evento.get('order_data', {})

    pedido_codigo = payload.get("codigo")
    pedido_id = payload.get("id")
    valor = payload.get("valor")
    logger.info(f"→ Iniciando processamento de pagamento para o pedido {pedido_codigo}")
    time.sleep(5)  # Simula o tempo de processamento

    # Logica para salvar o pagamento no banco de dados
    # Aqui você pode adicionar a lógica para salvar o pagamento no banco de dados
    create_log_payment_event(order_id=pedido_id, status="SUCCESS", valor=valor)

    publish_message({
        "evento": "PaymentProcessed",
        "codigo": pedido_codigo,
        "id": pedido_id,
        "valor": valor,
        "status": "SUCCESS",
        "data": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "metadata": {
            "source": "payment-service",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        }
    })

    logger.info(f"[✔] Pagamento processado com sucesso para o pedido {pedido_codigo}")

    # Confirma que a mensagem foi processada
    ch.basic_ack(delivery_tag=method.delivery_tag)


def process_payment_orders_creator_consumer():
    """Função principal para iniciar o consumidor RabbitMQ"""
    def consumer_thread():
        retries = 5
        delay = 5

        for attempt in range(retries):
            try:
                # Aguardar um pouco antes de tentar conectar
                if attempt > 0:
                    logger.info(f"Aguardando {delay} segundos antes de tentar novamente...")
                    time.sleep(delay)

                logger.info(f"💳 Tentativa {attempt + 1}/{retries} de conectar ao RabbitMQ...")
                connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
                channel = connection.channel()

                # Declara o exchange e a fila
                channel.exchange_declare(exchange='order.created', exchange_type='fanout', durable=True)
                queue_name = 'order_payment'
                channel.queue_declare(queue=queue_name, durable=True)
                channel.queue_bind(exchange='order.created', queue=queue_name)

                logger.info(f"[🎧] Aguardando eventos 'PedidoCriado' na fila {queue_name}...")

                # Define o callback para processar mensagens
                channel.basic_consume(queue=queue_name, on_message_callback=process_payment)

                # Inicia o consumo
                channel.start_consuming()
                break  # Se a conexão for bem-sucedida, sai do loop
            except Exception as e:
                logger.error(f"❌ Erro ao iniciar consumidor: {e}")
                time.sleep(delay)

    # Iniciar consumidor em thread separada para não bloquear a aplicação
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
    logger.info("Consumidor de eventos de 'PedidoCriado' iniciado em background")



    # logger.info("Conectando ao RabbitMQ...")
    # conexao = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    # canal = conexao.channel()

    # logger.info("Configurando consumidor da fila order_queue...")

    # # Declara o mesmo exchange usado pelo produtor
    # canal.exchange_declare(exchange='order.created', exchange_type='fanout', durable=True)

    # # Declara a fila (pode ser uma por serviço)
    # nome_fila = 'order_payment'
    # canal.queue_declare(queue=nome_fila, durable=True)

    # # Liga a fila ao exchange
    # canal.queue_bind(exchange='order.created', queue=nome_fila)

    # logger.info(f"[🎧] Aguardando eventos 'PedidoCriado' na fila {nome_fila}...")

    # # Define o callback para processar mensagens
    # canal.basic_consume(queue=nome_fila, on_message_callback=process_payment)

    # # Inicia o consumo
    # canal.start_consuming()
