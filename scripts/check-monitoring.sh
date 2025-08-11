#!/bin/bash

echo "🔍 Verificando setup do monitoramento..."

# Verificar se os serviços estão respondendo
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ Verificando $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name está respondendo"
            return 0
        fi
        echo "⏳ Tentativa $attempt/$max_attempts para $service_name..."
        sleep 2
        ((attempt++))
    done
    
    echo "❌ $service_name não está respondendo após $max_attempts tentativas"
    return 1
}

echo ""
echo "📊 Verificando serviços de monitoramento..."

# Verificar Prometheus
check_service "Prometheus" "http://localhost:9090/-/healthy"

# Verificar Grafana
check_service "Grafana" "http://localhost:3000/api/health"

echo ""
echo "🏗️ Verificando serviços da aplicação..."

# Verificar serviços da aplicação (através do API Gateway)
check_service "API Gateway" "http://localhost/"

echo ""
echo "📈 Verificando endpoints de métricas..."

# Verificar se os endpoints de métricas estão respondendo
services=("order-service:8000" "payment-service:8001" "notification-service:8002")

for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    # Tentar acessar métricas diretamente do container
    if docker exec ${service_name//-/_} curl -s http://localhost:$port/metrics > /dev/null 2>&1; then
        echo "✅ Métricas do $service_name estão disponíveis"
    else
        echo "❌ Métricas do $service_name não estão disponíveis"
    fi
done

echo ""
echo "🐰 Verificando RabbitMQ..."

# Verificar RabbitMQ Management
check_service "RabbitMQ Management" "http://localhost:15672/"

# Verificar se plugins do Prometheus estão habilitados
if docker exec tcc-rabbitmq rabbitmq-plugins list | grep -q "rabbitmq_prometheus.*E"; then
    echo "✅ Plugin Prometheus do RabbitMQ está habilitado"
else
    echo "⚠️  Plugin Prometheus do RabbitMQ não está habilitado"
    echo "💡 Execute: ./setup-rabbitmq-metrics.sh"
fi

# Verificar métricas do RabbitMQ
if curl -s "http://localhost:15692/metrics" > /dev/null 2>&1; then
    echo "✅ Métricas do RabbitMQ estão disponíveis"
else
    echo "❌ Métricas do RabbitMQ não estão disponíveis"
fi

echo ""
echo "🎯 URLs importantes:"
echo "   📊 Prometheus: http://localhost:9090"
echo "   📈 Grafana: http://localhost:3000 (admin/admin)"
echo "   🐰 RabbitMQ: http://localhost:15672 (guest/guest)"
echo "   🌐 API Gateway: http://localhost/"

echo ""
echo "🔧 Para testar as métricas:"
echo "   1. Faça algumas requisições para os serviços"
echo "   2. Acesse o Grafana e veja o dashboard 'TCC Project - Microservices Monitoring'"
echo "   3. Ou use o Prometheus para queries customizadas"

echo ""
echo "✅ Verificação concluída!"
