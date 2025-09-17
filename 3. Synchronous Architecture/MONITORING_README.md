# Monitoramento com Prometheus e Grafana

Este projeto inclui um sistema completo de monitoramento usando Prometheus para coleta de métricas e Grafana para visualização.

## 🚀 Como usar

### 1. Iniciar todos os serviços
```bash
docker-compose up -d
```

### 2. Configurar métricas do RabbitMQ
Após todos os containers estarem rodando, execute:
```bash
./setup-rabbitmq-metrics.sh
```

### 3. Acessar interfaces

#### Prometheus
- **URL**: http://localhost:9090
- **Descrição**: Interface para consultas de métricas
- **Uso**: Visualizar métricas brutas e testar queries

#### Grafana
- **URL**: http://localhost:3000
- **Login**: admin / admin
- **Descrição**: Dashboards para visualização das métricas
- **Dashboard**: "TCC Project - Microservices Monitoring"

#### RabbitMQ Management
- **URL**: http://localhost:15672
- **Login**: guest / guest
- **Métricas**: http://localhost:15692/metrics

## 📊 Métricas Coletadas

### Serviços (Order, Payment, Notification)
- `*_service_requests_total`: Total de requisições HTTP
- `*_service_request_duration_seconds`: Tempo de resposta das requisições
- `*_service_*_processed_total`: Total de operações processadas
- `*_service_rabbitmq_messages_total`: Mensagens RabbitMQ processadas

### PostgreSQL
- `pg_stat_database_*`: Estatísticas das bases de dados
- `pg_stat_bgwriter_*`: Estatísticas do background writer
- `pg_locks_*`: Informações sobre locks

### RabbitMQ
- `rabbitmq_queue_messages`: Mensagens nas filas
- `rabbitmq_connections`: Conexões ativas
- `rabbitmq_consumers`: Consumidores ativos

## 🎯 Endpoints de Métricas

Cada serviço expõe suas métricas no endpoint `/metrics`:

- **Order Service**: http://localhost/orders/metrics (via API Gateway)
- **Payment Service**: http://localhost/payments/metrics (via API Gateway)  
- **Notification Service**: http://localhost/notifications/metrics (via API Gateway)

## 📈 Queries Úteis no Prometheus

### Taxa de requisições por serviço
```promql
sum(rate(order_service_requests_total[5m])) by (service)
```

### Tempo de resposta P95
```promql
histogram_quantile(0.95, rate(payment_service_request_duration_seconds_bucket[5m]))
```

### Erros HTTP (status 4xx e 5xx)
```promql
sum(rate(order_service_requests_total{status=~"4..|5.."}[5m]))
```

### Mensagens na fila RabbitMQ
```promql
sum(rabbitmq_queue_messages) by (queue)
```

## 🔧 Configuração Personalizada

### Prometheus
Edite `prometheus/prometheus.yml` para:
- Ajustar intervalos de coleta
- Adicionar novos targets
- Configurar regras de alerta

### Grafana
- Dashboards adicionais podem ser adicionados em `grafana/dashboards/`
- Datasources em `grafana/datasources.yml`

## 🚨 Alertas (Futuro)

Para configurar alertas, adicione regras em `prometheus/alert-rules.yml`:

```yaml
groups:
  - name: microservices-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(order_service_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Alto número de erros no Order Service"
```

## 📝 Notas Importantes

1. **Performance**: As métricas têm impacto mínimo na performance dos serviços
2. **Armazenamento**: Prometheus mantém dados por 200h por padrão
3. **Segurança**: Em produção, configure autenticação adequada
4. **Backup**: Configure backup do volume `grafana-storage` para preservar dashboards

## 🔍 Troubleshooting

### RabbitMQ métricas não aparecendo
```bash
# Verificar se plugins estão habilitados
docker exec tcc-rabbitmq rabbitmq-plugins list

# Re-executar setup
./setup-rabbitmq-metrics.sh
```

### Grafana não mostra dados
1. Verificar se Prometheus está rodando: http://localhost:9090
2. Verificar se datasource está configurado corretamente
3. Verificar se os serviços estão expondo métricas nos endpoints `/metrics`
