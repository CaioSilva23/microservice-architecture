# Exemplo de Instrumentação Customizada

## Como adicionar métricas específicas de negócio

### 1. No arquivo principal (main.py)
Já configuramos as métricas básicas. Para métricas específicas, importe no router:

```python
from prometheus_client import Counter, Histogram, Gauge

# Métricas de negócio
PAYMENTS_BY_STATUS = Counter(
    'payment_service_payments_by_status_total',
    'Total payments by status',
    ['status']
)

PAYMENT_AMOUNT = Histogram(
    'payment_service_payment_amount',
    'Payment amounts distribution',
    buckets=[10, 50, 100, 500, 1000, 5000, 10000]
)

ACTIVE_PAYMENTS = Gauge(
    'payment_service_active_payments',
    'Number of active payments'
)
```

### 2. No router (payment_routers.py)
```python
from prometheus_client import Counter, Histogram
from main import PAYMENTS_BY_STATUS, PAYMENT_AMOUNT, ACTIVE_PAYMENTS

@router.post("/criar")
def create_payment(payment_data: PaymentCreate, db: Session = Depends(get_db)):
    try:
        # Lógica de criação do pagamento
        new_payment = Payment(**payment_data.dict())
        db.add(new_payment)
        db.commit()
        
        # Registrar métricas
        PAYMENTS_BY_STATUS.labels(status=new_payment.status).inc()
        PAYMENT_AMOUNT.observe(float(new_payment.amount))
        
        return new_payment
    except Exception as e:
        PAYMENTS_BY_STATUS.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    # Atualizar gauge com dados atuais
    active_count = db.query(Payment).filter(
        Payment.status.in_(["pending", "processing"])
    ).count()
    ACTIVE_PAYMENTS.set(active_count)
    
    return {"active_payments": active_count}
```

### 3. Métricas de Consumer (RabbitMQ)
```python
from main import RABBITMQ_MESSAGES

def process_payment_message(channel, method, properties, body):
    try:
        # Processar mensagem
        data = json.loads(body)
        
        # Registrar métrica de sucesso
        RABBITMQ_MESSAGES.labels(type="payment_order", status="success").inc()
        
        # Ack da mensagem
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Registrar métrica de erro
        RABBITMQ_MESSAGES.labels(type="payment_order", status="error").inc()
        
        # Reject da mensagem
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
```

### 4. Métricas de Database
```python
DB_QUERIES = Counter(
    'payment_service_db_queries_total',
    'Total database queries',
    ['operation', 'table']
)

DB_QUERY_DURATION = Histogram(
    'payment_service_db_query_duration_seconds',
    'Database query duration',
    ['operation', 'table']
)

# Decorator para instrumentar queries
def instrument_db_query(operation: str, table: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                DB_QUERIES.labels(operation=operation, table=table).inc()
                return result
            finally:
                duration = time.time() - start_time
                DB_QUERY_DURATION.labels(
                    operation=operation, 
                    table=table
                ).observe(duration)
        return wrapper
    return decorator

# Uso:
@instrument_db_query("select", "payments")
def get_payments(db: Session):
    return db.query(Payment).all()
```

### 5. Queries Úteis para Business Metrics

```promql
# Taxa de pagamentos aprovados vs rejeitados
rate(payment_service_payments_by_status_total{status="approved"}[5m]) /
rate(payment_service_payments_by_status_total{status="rejected"}[5m])

# Distribuição de valores de pagamento
histogram_quantile(0.95, payment_service_payment_amount_bucket)

# Tempo médio de processamento de pagamentos
avg(payment_service_request_duration_seconds{endpoint="/payments/processar"})

# Filas com mais mensagens
topk(5, rabbitmq_queue_messages)
```

### 6. Alertas Sugeridos

```yaml
# prometheus/alert-rules.yml
groups:
  - name: business-alerts
    rules:
      - alert: HighPaymentFailureRate
        expr: |
          rate(payment_service_payments_by_status_total{status="failed"}[5m]) /
          rate(payment_service_payments_by_status_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Taxa de falha de pagamentos alta"
          
      - alert: PaymentQueueBacklog
        expr: rabbitmq_queue_messages{queue="payment_queue"} > 100
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Backlog alto na fila de pagamentos"
```
