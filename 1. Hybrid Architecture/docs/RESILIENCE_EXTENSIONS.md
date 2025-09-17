# 🚀 Extensões de Resiliência e Monitoramento

## 📋 Visão Geral

Este documento descreve as extensões implementadas para completar o sistema de monitoramento, incluindo:

- ✅ **Health Checks** em todos os serviços
- ✅ **Circuit Breakers** para isolamento de falhas
- ✅ **Métricas de Uptime/Downtime**
- ✅ **Métricas de tempo de recuperação**
- ✅ **Métricas de dependências entre serviços**
- ✅ **Alertas automáticos**
- ✅ **Dashboard enhanced do Grafana**

## 🏥 Health Checks

### Implementação
Cada serviço agora possui um endpoint `/health` que verifica:
- Conectividade com banco de dados
- Conectividade com RabbitMQ
- Status geral do serviço

### Métricas Geradas
```promql
# Status de saúde (1=healthy, 0=unhealthy)
order_service_health_status
payment_service_health_status
notification_service_health_status
```

### Exemplo de Resposta
```json
{
  "status": "healthy",
  "timestamp": 1628720400.123,
  "uptime": 3600.5,
  "dependencies": {
    "database": "healthy",
    "rabbitmq": "healthy"
  }
}
```

## 🔌 Circuit Breakers

### Funcionalidades
- **Detecção automática** de falhas repetidas
- **Fail-fast** quando dependências estão indisponíveis
- **Recuperação automática** após timeout configurado
- **Métricas detalhadas** de estado e performance

### Estados
- `CLOSED (0)`: Operação normal
- `OPEN (1)`: Circuito aberto, falhando rapidamente
- `HALF_OPEN (2)`: Testando recuperação

### Métricas Geradas
```promql
# Estado do circuit breaker por dependência
order_service_circuit_breaker_state{dependency="database"}
payment_service_circuit_breaker_state{dependency="rabbitmq"}

# Chamadas para dependências
order_service_dependency_calls_total{dependency="database",status="success"}
payment_service_dependency_calls_total{dependency="rabbitmq",status="failure"}
```

### Configuração
```python
# Exemplo de circuit breaker para banco de dados
database_circuit_breaker = CircuitBreaker(
    name="payment_database",
    failure_threshold=3,  # Abre após 3 falhas
    timeout=30.0         # Tenta recuperar após 30s
)
```

## ⏱️ Métricas de Uptime e Tempo de Recuperação

### Uptime por Serviço
```promql
# Tempo de atividade em segundos
order_service_uptime_seconds
payment_service_uptime_seconds
notification_service_uptime_seconds
```

### Tempo de Recuperação
```promql
# Distribuição do tempo de recuperação
histogram_quantile(0.95, rate(payment_service_recovery_time_seconds_bucket[5m]))
histogram_quantile(0.50, rate(order_service_recovery_time_seconds_bucket[5m]))
```

## 🔗 Métricas de Desacoplamento

### Comunicação Assíncrona
```promql
# Sucesso/falha no processamento de mensagens
order_service_rabbitmq_messages_total{type="payment_order",status="success"}
payment_service_rabbitmq_messages_total{type="payment_order",status="error"}

# Profundidade das filas
rabbitmq_queue_messages{queue="order_payment"}
```

### Taxa de Sucesso de Dependências
```promql
# Taxa de sucesso por dependência
sum(rate(payment_service_dependency_calls_total{status="success"}[5m])) /
sum(rate(payment_service_dependency_calls_total[5m]))
```

## 🚨 Sistema de Alertas

### Grupos de Alertas Implementados

#### 1. Health Alerts
- **ServiceDown**: Serviço completamente indisponível
- **ServiceUnhealthy**: Health check falhando

#### 2. Performance Alerts
- **HighResponseTime**: Latência P95 > 2 segundos
- **HighErrorRate**: Taxa de erro HTTP 5xx > 5%

#### 3. Circuit Breaker Alerts
- **CircuitBreakerOpen**: Circuit breaker em estado aberto
- **CircuitBreakerHalfOpen**: Circuit breaker testando recuperação

#### 4. Dependency Alerts
- **LowDependencySuccessRate**: Taxa de sucesso < 90%
- **HighMessageQueueDepth**: Muitas mensagens acumuladas

#### 5. Recovery Alerts
- **SlowRecoveryTime**: Tempo de recuperação P95 > 10 segundos

#### 6. Business Alerts
- **HighMessageProcessingFailureRate**: Falha no processamento > 10%

### Exemplo de Alerta
```yaml
- alert: CircuitBreakerOpen
  expr: payment_service_circuit_breaker_state == 1
  for: 0s
  labels:
    severity: critical
  annotations:
    summary: "Circuit breaker is open"
    description: "Circuit breaker for {{ $labels.dependency }} is open"
```

## 📊 Dashboard Enhanced do Grafana

### Novos Painéis Adicionados

1. **Service Health Status**: Status em tempo real
2. **Service Uptime**: Tempo de atividade
3. **Circuit Breaker Status**: Estado dos circuit breakers
4. **HTTP Error Rate**: Taxa de erros 5xx
5. **Message Queue Processing**: Processamento de mensagens
6. **Recovery Time Distribution**: Distribuição do tempo de recuperação
7. **Dependency Call Success Rate**: Taxa de sucesso das dependências
8. **RabbitMQ Queue Depth**: Profundidade das filas

### Recursos do Dashboard
- **Visualização em tempo real** com refresh de 5s
- **Mapeamento de estados** (Healthy/Unhealthy, Circuit Breaker states)
- **Múltiplas séries temporais** para comparação
- **Percentis de latência** (P50, P95)

## 🧪 Como Testar

### 1. Script Automatizado
```bash
./test-resilience.sh
```

### 2. Testes Manuais

#### Testar Health Checks
```bash
# Verificar health check de cada serviço
curl http://localhost/orders/health
curl http://localhost/payments/health
curl http://localhost/notifications/health
```

#### Simular Falhas
```bash
# Parar banco de dados para testar circuit breaker
docker-compose stop db-payment-service

# Verificar métricas de circuit breaker
curl http://localhost/payments/metrics | grep circuit_breaker_state
```

#### Verificar Alertas
```bash
# Acessar alertas no Prometheus
curl http://localhost:9090/api/v1/alerts
```

## 📈 Queries Úteis

### Availabilidade por Serviço
```promql
avg_over_time(order_service_health_status[1h]) * 100
```

### MTTR (Mean Time To Recovery)
```promql
avg(payment_service_recovery_time_seconds)
```

### Taxa de Falha de Circuit Breakers
```promql
sum(rate(payment_service_dependency_calls_total{status="failure"}[5m])) /
sum(rate(payment_service_dependency_calls_total[5m]))
```

### Isolamento de Falhas (Circuit Breaker Efficiency)
```promql
sum(increase(payment_service_circuit_breaker_state[1h]) > 0) /
sum(increase(payment_service_dependency_calls_total{status="failure"}[1h])) * 100
```

## 🔧 Configuração e Customização

### Ajustar Circuit Breaker
```python
# No arquivo shared/circuit_breaker.py
CircuitBreaker(
    name="custom_dependency",
    failure_threshold=5,    # Número de falhas para abrir
    timeout=60.0,          # Tempo para tentar recuperar (segundos)
    expected_exception=Exception  # Tipo de exceção a tratar
)
```

### Adicionar Novas Métricas
```python
# No main.py de cada serviço
CUSTOM_METRIC = Counter(
    'service_custom_operations_total',
    'Description of custom metric',
    ['label1', 'label2']
)
```

### Personalizar Alertas
Edite o arquivo `prometheus/alert-rules.yml` para adicionar novos alertas ou ajustar thresholds.

## 📝 Resumo de Atendimento aos Requisitos

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| **Tempo de resposta médio** | ✅ Completo | Histograms P50, P95, P99 |
| **Taxa de falhas HTTP 5xx** | ✅ Completo | Counters por status code |
| **Taxa de falhas mensageria** | ✅ Completo | Counters success/error |
| **Isolamento de falhas** | ✅ Completo | Circuit breakers automáticos |
| **Desacoplamento** | ✅ Completo | Métricas de filas e dependências |
| **Tempo de recuperação** | ✅ Completo | Histograms de recovery time |

## 🎯 Próximos Passos

1. **Implementar distributed tracing** (Jaeger/Zipkin)
2. **Adicionar logs centralizados** (ELK Stack)
3. **Implementar chaos engineering** (Chaos Monkey)
4. **Adicionar testes de carga automatizados** (k6/Locust)
5. **Implementar blue-green deployment** com métricas

## 📞 Troubleshooting

### Circuit Breakers não funcionando
1. Verificar se as dependências estão registradas
2. Verificar logs dos serviços
3. Confirmar que as exceções estão sendo capturadas

### Métricas não aparecendo
1. Verificar se endpoints `/metrics` estão acessíveis
2. Confirmar configuração do Prometheus
3. Verificar logs do Prometheus

### Alertas não disparando
1. Verificar sintaxe das regras de alerta
2. Confirmar que o Prometheus carregou as regras
3. Verificar se as métricas necessárias existem

---

**📧 Para suporte adicional, consulte os logs dos serviços e a documentação do Prometheus/Grafana.**
